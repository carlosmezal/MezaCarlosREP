"""
ml_models.py — Módulo de Machine Learning
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing   import StandardScaler, LabelEncoder
from sklearn.metrics         import accuracy_score, f1_score, classification_report
from sklearn.linear_model    import LogisticRegression
from sklearn.neighbors       import KNeighborsClassifier
from sklearn.svm             import SVC
from sklearn.ensemble        import RandomForestClassifier
from sklearn.tree            import DecisionTreeClassifier
from sklearn.cluster         import KMeans
from sklearn.decomposition   import PCA


ALL_MODELS = {
    "Logistic Regression": lambda: LogisticRegression(
        max_iter=500, random_state=42
    ),
    "KNN (k=5)": lambda: KNeighborsClassifier(
        n_neighbors=5, n_jobs=-1
    ),
    "SVM (RBF)": lambda: SVC(
        kernel="rbf", random_state=42,
        max_iter=2000,     # límite duro: sin esto, SVC puede tardar
                            # muchísimo (o sentirse "colgado") en datos
                            # difíciles de separar
        cache_size=300
    ),
    "Random Forest": lambda: RandomForestClassifier(
        n_estimators=60, random_state=42, n_jobs=-1
    ),
    "Decision Tree": lambda: DecisionTreeClassifier(
        max_depth=5, random_state=42
    ),
}


class MLManager:
    """
    Gestiona todas las operaciones de Machine Learning.

    """

    def __init__(self):
        self.scaler = StandardScaler()

    # ── Preparación de datos ──────────────────────────────────── #
    def _prepare(self, df, target_col):
        """
        Separa features (X) y target (y), escala X con StandardScaler
        y codifica y con LabelEncoder si es categórico.

        Retorna: X_tr, X_te, y_tr, y_te, feat_cols, classes
        """
        num_cols  = df.select_dtypes(include="number").columns.tolist()
        feat_cols = [c for c in num_cols if c != target_col]

        if not feat_cols:
            raise ValueError("No hay columnas numéricas disponibles como features.")

        subset = df[feat_cols + [target_col]].dropna()
        if len(subset) < 10:
            raise ValueError(f"Solo {len(subset)} registros válidos — se necesitan al menos 10.")

        MAX_ROWS = 5000
        if len(subset) > MAX_ROWS:
            subset = subset.sample(n=MAX_ROWS, random_state=42)

        X     = subset[feat_cols].values
        y_raw = subset[target_col].values

        le = LabelEncoder()
        y  = le.fit_transform(y_raw.astype(str))

        X_sc = self.scaler.fit_transform(X)

        try:
            X_tr, X_te, y_tr, y_te = train_test_split(
                X_sc, y, test_size=0.2, random_state=42, stratify=y
            )
        except ValueError:
            X_tr, X_te, y_tr, y_te = train_test_split(
                X_sc, y, test_size=0.2, random_state=42
            )

        return X_tr, X_te, y_tr, y_te, feat_cols, le.classes_

    # ── Entrenar modelos seleccionados (detallado) ────────────── #
    def train_models(self, df, target_col, model_names, cancel_check=None,
                      progress_callback=None):
        """
        Entrena los modelos
        """
        X_tr, X_te, y_tr, y_te, feat_cols, classes = self._prepare(df, target_col)
        resultados = []
        cancelado  = False
        total      = len(model_names)

        for i, nombre in enumerate(model_names, 1):
            if cancel_check and cancel_check():
                cancelado = True
                break

            if progress_callback:
                progress_callback(nombre, i, total)

            modelo = ALL_MODELS[nombre]()
            modelo.fit(X_tr, y_tr)
            y_pred = modelo.predict(X_te)

            acc = accuracy_score(y_te, y_pred)
            f1  = f1_score(y_te, y_pred, average="weighted", zero_division=0)
            rep = classification_report(
                y_te, y_pred,
                target_names=[str(c) for c in classes],
                zero_division=0
            )

            # Importancia de features (solo RF y DT la tienen)
            importances = None
            if hasattr(modelo, "feature_importances_"):
                importances = dict(
                    sorted(
                        zip(feat_cols, modelo.feature_importances_),
                        key=lambda x: x[1], reverse=True
                    )
                )

            resultados.append({
                "nombre":      nombre,
                "accuracy":    round(acc, 4),
                "f1":          round(f1, 4),
                "report":      rep,
                "importances": importances,
                "train":       len(X_tr),
                "test":        len(X_te),
            })

        return resultados, feat_cols, list(classes), cancelado

    # ── Comparar modelos (tabla resumen) ─────────────────────── #
    def compare_models(self, df, target_col, model_names, cancel_check=None,
                        progress_callback=None):
        """
        Entrena los modelos indicados y devuelve una tabla comparativa
     
        """
        X_tr, X_te, y_tr, y_te, feat_cols, classes = self._prepare(df, target_col)
        filas     = []
        mejor_acc = -1
        mejor     = ""
        mejor_rep = ""
        cancelado = False
        total     = len(model_names)

        for i, nombre in enumerate(model_names, 1):
            if cancel_check and cancel_check():
                cancelado = True
                break

            if progress_callback:
                progress_callback(nombre, i, total)

            modelo = ALL_MODELS[nombre]()
            modelo.fit(X_tr, y_tr)
            y_pred = modelo.predict(X_te)

            acc = accuracy_score(y_te, y_pred)
            f1  = f1_score(y_te, y_pred, average="weighted", zero_division=0)

            filas.append({
                "Modelo":   nombre,
                "Accuracy": round(acc, 4),
                "F1 Score": round(f1, 4),
                "Train":    len(X_tr),
                "Test":     len(X_te),
            })

            if acc > mejor_acc:
                mejor_acc = acc
                mejor     = nombre
                mejor_rep = classification_report(
                    y_te, y_pred,
                    target_names=[str(c) for c in classes],
                    zero_division=0
                )

        df_res = pd.DataFrame(filas)
        if not df_res.empty:
            df_res = df_res.sort_values("Accuracy", ascending=False).reset_index(drop=True)

        return df_res, feat_cols, list(classes), mejor, mejor_rep, cancelado

    # ── Clustering K-Means + PCA ─────────────────────────────── #
    def cluster_and_pca(self, df, n_clusters=3):
        """
        Aplica K-Means (clustering) + PCA (reducción a 2D).
        """
        num_cols = df.select_dtypes(include="number").columns.tolist()
        if len(num_cols) < 2:
            raise ValueError("Se necesitan al menos 2 columnas numéricas para PCA.")

        subset = df[num_cols].dropna()
        if len(subset) < n_clusters:
            raise ValueError(f"Muy pocos registros ({len(subset)}) para {n_clusters} clusters.")

        X_sc = self.scaler.fit_transform(subset.values)

        n_comp = min(2, len(num_cols))
        pca    = PCA(n_components=n_comp)
        X_pca  = pca.fit_transform(X_sc)
        var    = [round(v * 100, 2) for v in pca.explained_variance_ratio_]

        km      = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = km.fit_predict(X_sc)

        df_res = df.copy()
        idx    = subset.index
        df_res.loc[idx, "cluster"] = clusters.astype(int)
        df_res.loc[idx, "PCA_1"]   = X_pca[:, 0].round(4)
        if n_comp > 1:
            df_res.loc[idx, "PCA_2"] = X_pca[:, 1].round(4)

        return df_res, var, num_cols, round(km.inertia_, 2)

    # ── Sugerir columnas target ───────────────────────────────── #
    def get_target_candidates(self, df):
        """Columnas con pocos valores únicos — buenas candidatas para target."""
        cands = []
        for col in df.columns:
            nu = df[col].nunique()
            if str(df[col].dtype) == "bool" or 2 <= nu <= 20:
                cands.append(col)
        return cands if cands else list(df.columns)

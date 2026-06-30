-- ══════════════════════════════════════════════════════════════
--  setup.sql — Base de datos Pokémon para DataAnalyzer
--  Ejecutar: psql -U postgres -f sql/setup.sql
-- ══════════════════════════════════════════════════════════════

CREATE DATABASE pokedex;
\c pokedex

-- ──────────────────────────────────────────────────────────────
--  TABLA: pokemon
-- ──────────────────────────────────────────────────────────────
CREATE TABLE pokemon (
    numero       INTEGER PRIMARY KEY,
    nombre       VARCHAR(50)  NOT NULL,
    tipo1        VARCHAR(20)  NOT NULL,
    tipo2        VARCHAR(20),
    hp           INTEGER,
    ataque       INTEGER,
    defensa      INTEGER,
    sp_ataque    INTEGER,
    sp_defensa   INTEGER,
    velocidad    INTEGER,
    generacion   INTEGER,
    legendario   BOOLEAN DEFAULT FALSE
);

INSERT INTO pokemon VALUES
(1,  'Bulbasaur',  'Grass',    'Poison',  45,  49,  49,  65,  65,  45,  1, FALSE),
(2,  'Ivysaur',    'Grass',    'Poison',  60,  62,  63,  80,  80,  60,  1, FALSE),
(3,  'Venusaur',   'Grass',    'Poison',  80,  82,  83,  100, 100, 80,  1, FALSE),
(4,  'Charmander', 'Fire',     NULL,      39,  52,  43,  60,  50,  65,  1, FALSE),
(5,  'Charmeleon', 'Fire',     NULL,      58,  64,  58,  80,  65,  80,  1, FALSE),
(6,  'Charizard',  'Fire',     'Flying',  78,  84,  78,  109, 85,  100, 1, FALSE),
(7,  'Squirtle',   'Water',    NULL,      44,  48,  65,  50,  64,  43,  1, FALSE),
(9,  'Blastoise',  'Water',    NULL,      79,  83,  100, 85,  105, 78,  1, FALSE),
(25, 'Pikachu',    'Electric', NULL,      35,  55,  40,  50,  50,  90,  1, FALSE),
(26, 'Raichu',     'Electric', NULL,      60,  90,  55,  90,  80,  110, 1, FALSE),
(39, 'Jigglypuff', 'Normal',   'Fairy',   115, 45,  20,  45,  25,  20,  1, FALSE),
(52, 'Meowth',     'Normal',   NULL,      40,  45,  35,  40,  40,  90,  1, FALSE),
(54, 'Psyduck',    'Water',    NULL,      50,  52,  48,  65,  50,  55,  1, FALSE),
(94, 'Gengar',     'Ghost',    'Poison',  60,  65,  60,  130, 75,  110, 1, FALSE),
(113,'Chansey',    'Normal',   NULL,      250, 5,   5,   35,  105, 50,  1, FALSE),
(130,'Gyarados',   'Water',    'Flying',  95,  125, 79,  60,  100, 81,  1, FALSE),
(131,'Lapras',     'Water',    'Ice',     130, 85,  80,  85,  95,  60,  1, FALSE),
(132,'Ditto',      'Normal',   NULL,      48,  48,  48,  48,  48,  48,  1, FALSE),
(133,'Eevee',      'Normal',   NULL,      55,  55,  50,  45,  65,  55,  1, FALSE),
(143,'Snorlax',    'Normal',   NULL,      160, 110, 65,  65,  110, 30,  1, FALSE),
(144,'Articuno',   'Ice',      'Flying',  90,  85,  100, 95,  125, 85,  1, TRUE),
(145,'Zapdos',     'Electric', 'Flying',  90,  90,  85,  125, 90,  100, 1, TRUE),
(146,'Moltres',    'Fire',     'Flying',  90,  100, 90,  125, 85,  90,  1, TRUE),
(149,'Dragonite',  'Dragon',   'Flying',  91,  134, 95,  100, 100, 80,  1, FALSE),
(150,'Mewtwo',     'Psychic',  NULL,      106, 110, 90,  154, 90,  130, 1, TRUE),
(151,'Mew',        'Psychic',  NULL,      100, 100, 100, 100, 100, 100, 1, TRUE),
(196,'Espeon',     'Psychic',  NULL,      65,  65,  60,  130, 95,  110, 2, FALSE),
(197,'Umbreon',    'Dark',     NULL,      95,  65,  110, 60,  130, 65,  2, FALSE),
(245,'Suicune',    'Water',    NULL,      100, 75,  115, 90,  115, 85,  2, TRUE),
(249,'Lugia',      'Psychic',  'Flying',  106, 90,  130, 90,  154, 110, 2, TRUE),
(250,'Ho-Oh',      'Fire',     'Flying',  106, 130, 90,  110, 154, 90,  2, TRUE),
(282,'Gardevoir',  'Psychic',  'Fairy',   68,  65,  65,  125, 115, 80,  3, FALSE),
(330,'Flygon',     'Dragon',   'Ground',  80,  100, 80,  80,  80,  100, 3, FALSE),
(350,'Milotic',    'Water',    NULL,      95,  60,  79,  100, 125, 81,  3, FALSE),
(384,'Rayquaza',   'Dragon',   'Flying',  105, 150, 90,  150, 90,  95,  3, TRUE),
(448,'Lucario',    'Fighting', 'Steel',   70,  110, 70,  115, 70,  90,  4, FALSE),
(483,'Dialga',     'Steel',    'Dragon',  100, 120, 120, 150, 100, 90,  4, TRUE),
(484,'Palkia',     'Water',    'Dragon',  90,  120, 100, 150, 120, 100, 4, TRUE),
(487,'Giratina',   'Ghost',    'Dragon',  150, 100, 120, 100, 120, 90,  4, TRUE),
(644,'Zekrom',     'Dragon',   'Electric',100, 150, 120, 120, 100, 90,  5, TRUE),
(646,'Kyurem',     'Dragon',   'Ice',     125, 130, 90,  130, 90,  95,  5, TRUE);

CREATE TABLE tipos (
    tipo            VARCHAR(20) PRIMARY KEY,
    ventaja_contra  TEXT,
    debil_contra    TEXT,
    inmune_a        TEXT
);

INSERT INTO tipos VALUES
('Normal',   'ninguno',                        'Fighting',                   'Ghost'),
('Fire',     'Grass,Bug,Ice,Steel',             'Water,Ground,Rock',          NULL),
('Water',    'Fire,Ground,Rock',                'Grass,Electric',             NULL),
('Electric', 'Water,Flying',                   'Ground',                     'Ground'),
('Grass',    'Water,Ground,Rock',               'Fire,Ice,Poison,Flying,Bug', NULL),
('Ice',      'Grass,Ground,Flying,Dragon',      'Fire,Fighting,Rock,Steel',   NULL),
('Fighting', 'Normal,Ice,Rock,Dark,Steel',      'Flying,Psychic,Fairy',       NULL),
('Poison',   'Grass,Fairy',                    'Ground,Psychic',             NULL),
('Ground',   'Fire,Electric,Poison,Rock,Steel', 'Water,Grass,Ice',            'Electric'),
('Flying',   'Grass,Fighting,Bug',              'Electric,Ice,Rock',          'Ground'),
('Psychic',  'Fighting,Poison',                'Bug,Ghost,Dark',             NULL),
('Bug',      'Grass,Psychic,Dark',              'Fire,Flying,Rock',           NULL),
('Rock',     'Fire,Ice,Flying,Bug',             'Water,Grass,Fighting,Ground,Steel', NULL),
('Ghost',    'Psychic,Ghost',                  'Ghost,Dark',                 'Normal,Fighting'),
('Dragon',   'Dragon',                         'Ice,Dragon,Fairy',           NULL),
('Dark',     'Psychic,Ghost',                  'Fighting,Bug,Fairy',         'Psychic'),
('Steel',    'Ice,Rock,Fairy',                 'Fire,Fighting,Ground',       'Poison'),
('Fairy',    'Fighting,Dragon,Dark',            'Poison,Steel',               'Dragon');

-- Consultas de prueba:
-- SELECT * FROM pokemon ORDER BY numero;
-- SELECT nombre, tipo1, ataque FROM pokemon WHERE legendario = TRUE ORDER BY ataque DESC;
-- SELECT generacion, COUNT(*) as total, ROUND(AVG(ataque),1) as atk_prom FROM pokemon GROUP BY generacion ORDER BY generacion;
-- SELECT nombre, tipo1, tipo2, GREATEST(ataque,sp_ataque) AS mejor_atk FROM pokemon ORDER BY mejor_atk DESC LIMIT 10;

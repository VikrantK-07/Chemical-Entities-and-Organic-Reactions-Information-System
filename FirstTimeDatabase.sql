CREATE TABLE ChemLib;

use ChemLib;

CREATE TABLE chemicals (
    formula varchar(50)  DEFAULT NULL,
    common varchar(100) DEFAULT NULL,
    iupac varchar(100) DEFAULT NULL,
    MW float DEFAULT NULL,
    CAS varchar(25) UNIQUE DEFAULT NULL,
    smiles varchar(50) DEFAULT NULL,
    pubchemid varchar(50) DEFAULT NULL,
    carcinogen varchar(50) DEFAULT NULL,
    skin varchar(4) DEFAULT NULL,
    BP float DEFAULT NULL,
    MP float DEFAULT NULL,
    flash float DEFAULT NULL,
    image_path varchar(100) DEFAULT NULL,
    synonyms varchar(200) DEFAULT NULL
);



CREATE TABLE userauth (
    username varchar(25) DEFAULT NULL,
    password varchar(25) DEFAULT NULL
);

INSERT INTO userauth values('admin','admin');

CREATE TABLE wiki_data (
    id int NOT NULL PRIMARY KEY AUTO_INCREMENT,
    title varchar(255) DEFAULT NULL,
    overview text DEFAULT NULL,
    image_path varchar(500) DEFAULT NULL
);
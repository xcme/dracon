CREATE TABLE `configs` (
    `hash` CHAR(32) NOT NULL,
    `config` BLOB NULL,
    UNIQUE INDEX `hash` (`hash`)
)
COLLATE='latin1_swedish_ci'
ENGINE=InnoDB
;

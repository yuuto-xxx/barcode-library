CREATE TABLE manger(
    mail varchar(256) not null,
    name varchar(64) not null,
    password varchar(64) not null,
    salt varchar(32) not null,
    password_flag boolean not null default false,
    delete_flag boolean not null default false,
    primary key(mail)
);
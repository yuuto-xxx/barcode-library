#�w�ȃe�[�u��
create table course (course_id varchar(2) not null primary key, course_name varchar(32) not null, max_year int not null);

insert into course values('1', '���V�X�e����',2);
insert into course values('2', '',);

#�w���e�[�u��
create table student (stu_number int not null primary key,
mail varchar(256) not null,
name varchar(64) not null unique,
password varchar(64) not null,
salt varchar(32) not null,
course_id varchar(2) not null,
year int not null,
password_flag boolean not null default True,
delete_flag boolean not null default false,
foreign key (course_id) references course(course_id));

#�Ǘ��҃e�[�u��
create table manager (mail varchar(256) not null primary key,
name varchar(64) not null,
password varchar(64) not null,
salt varchar(32) not null,
password_flag boolean not null default true,
delete_flag boolean not null default false);

#�i�������e�[�u��
create table promotion_history(promotion_id serial not null primary key,
promotion_day date not null,
manager_mail varchar(256) not null,
foreign key (manager_mail) references manager(mail));

#�u�b�N�e�[�u��
create table book(book_isbn varchar(13) not null primary key,
image varchar(128),
title varchar(128) not null,
author varchar(64),
publisher varchar(64),
release_day date,
amount_max int not null,
book_delete_flag boolean not null default false);

#���r���[�e�[�u��
create table review (book_isbn varchar(13) not null,
stu_number int not null,
review_comment varchar(1024),
review_star int not null,
name_flag boolean not null default false,
foreign key(book_isbn) references book(book_isbn),
foreign key(stu_number) references student(stu_number));

#�؂�Ă���{�e�[�u��
create table rent_book (stu_number int not null,
book_isbn varchar(13) not null,
rent_day date not null,
return_day date,
amount int not null default 1,
foreign key(stu_number) references student(stu_number),
foreign key(book_isbn) references book(book_isbn));

#�^�O���ԃe�[�u��
create table book_tag (book_isbn varchar(13) not null,
tag_id int not null,
primary key(book_isbn,tag_id),
foreign key(book_isbn) references book(book_isbn),
foreign key(tag_id) references tag(tag_id));

#�^�O�e�[�u��
create table tag (tag_id serial not null primary key,
tag_name varchar(16) not null);
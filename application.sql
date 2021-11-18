-- 学科テーブル
create table course (course_id varchar(2) not null primary key, course_name varchar(32) not null, max_year int not null);

insert into course values('1', '情報システム科',2);
insert into course values('2', 'ネットワークセキュリティ科',2);
insert into course values('3', '総合システム工学科',3);
insert into course values('4', '高度情報工学科',4);
insert into course values('5', '情報ビジネス科',2);
insert into course values('6', 'グラフィックデザインコース',2);
insert into course values('7', 'アニメ・マンガコース',2);
insert into course values('8', 'CGクリエイトコース',2);
insert into course values('9', '建築インテリアコース',2);
insert into course values('10', '総合デザイン科',3);

-- 学生テーブル
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

-- 管理者テーブル
create table manager (mail varchar(256) not null primary key,
name varchar(64) not null,
password varchar(64) not null,
salt varchar(32) not null,
password_flag boolean not null default true,
delete_flag boolean not null default false);

-- 進級履歴テーブル
create table promotion_history(promotion_id serial not null primary key,
promotion_day date not null,
manager_mail varchar(256) not null,
foreign key (manager_mail) references manager(mail));

-- 本テーブル
create table book(book_isbn varchar(13) not null primary key,
image varchar(128),
title varchar(128) not null,
author varchar(64),
publisher varchar(64),
release_day date,
amount_max int not null,
book_delete_flag boolean not null default false);

-- レビューテーブル
create table review (book_isbn varchar(13) not null,
stu_number int not null,
review_comment varchar(1024),
review_star int not null,
name_flag boolean not null default false,
foreign key(book_isbn) references book(book_isbn),
foreign key(stu_number) references student(stu_number));

-- 借りている本テーブル
create table rent_book (stu_number int not null,
book_isbn varchar(13) not null,
rent_day date not null,
return_day date,
amount int not null default 1,
foreign key(stu_number) references student(stu_number),
foreign key(book_isbn) references book(book_isbn));

-- 中間テーブル
create table book_tag (book_isbn varchar(13) not null,
tag_id int not null,
primary key(book_isbn,tag_id),
foreign key(book_isbn) references book(book_isbn),
foreign key(tag_id) references tag(tag_id));

-- タグテーブル
create table tag (tag_id serial not null primary key,
tag_name varchar(16) not null);
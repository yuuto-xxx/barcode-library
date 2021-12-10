-- 本のテストデータ

insert into book(book_isbn,title,amount_max) values('9784295007807', 'Java', 5);

-- tagのテストデータ
insert into tag(tag_name) values ('基本情報');
insert into tag(tag_name) values ('試験');
insert into tag(tag_name) values ('Java');
insert into tag(tag_name) values ('Go');
insert into tag(tag_name) values ('プログラミング基礎');
insert into tag(tag_name) values ('HTML');
insert into tag(tag_name) values ('PHP');
insert into tag(tag_name) values ('Python');
insert into tag(tag_name) values ('デザイン入門');
insert into tag(tag_name) values ('CSS');
insert into tag(tag_name) values ('ビジネスマナー');
insert into tag(tag_name) values ('AI');

insert into book_tag(book_isbn,tag_id) values ('9784798162508',8);
insert into book_tag(book_isbn,tag_id) values ('9784295006329',8);
insert into book_tag(book_isbn,tag_id) values ('9784815601577',5);

insert into book_tag(book_isbn,tag_id) values ('9784295006329',5);
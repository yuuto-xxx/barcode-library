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

select stu_number,name,course_name from 
student join course on (student.course_id=course.course_id) where
(((student.course_id='3' or student.course_id='10') and year=3)
or (student.course_id='4' and year=4)
or (student.course_id<>'3' and student.course_id<>'4' and student.course_id<>'10' and year=2))
and student.delete_flag=false;

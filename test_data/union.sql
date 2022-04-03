create assertion foo check
(
    not exists (
        (select sid as temp from instruct where sid not in (select * from student))
        union
        (select iid as temp from instruct where iid not in (select * from professor))
    )
)
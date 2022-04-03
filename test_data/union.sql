CREATE ASSERTION foo CHECK(
    NOT EXISTS(
        (SELECT sid AS temp FROM instruct WHERE sid NOT IN (
            SELECT * FROM student
        )) 
        UNION
        (SELECT iid AS temp FROM instruct WHERE iid NOT IN (
            SELECT * FROM professor
        ))
    )
)
CREATE assertion single_table_assertion CHECK (
    NOT EXISTS (
        SELECT
            *
        FROM
            mytable1
        where
            id = 1;

)
);

CREATE assertion multiple_table_assertion CHECK (
    EXISTS (
        SELECT
            *
        FROM
            mytable1 t1
            join mytable2 t2 on t1.ID = t2.ID
        where
            mytable1.Name = 'Tom';

)
);
CREATE assertion single_table_assertion CHECK (
    1 < (
        SELECT
            COUNT(*)
        FROM
            table1
    )
);

CREATE assertion single_table_assertion CHECK (
    table1.ID = table2.ID
);

CREATE assertion single_table_assertion CHECK (
    table1.ID = table2.ID
);


CREATE assertion single_table_assertion_not CHECK (
    NOT (
        (table1.ID = table2.ID)
        OR
        (table3.ID = table4.ID)
    )
);

CREATE assertion single_table_assertion_brackets CHECK (
    (table1.ID = table2.ID)
    OR
    table3.ID = table4.ID
);
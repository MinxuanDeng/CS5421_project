
CREATE assertion single_table_assertion CHECK (
    table1.ID = table2.ID
);
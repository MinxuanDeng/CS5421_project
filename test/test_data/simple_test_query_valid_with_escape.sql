CREATE assertion single_table_assertion CHECK (
	EXISTS (
		SELECT
			id
		FROM
			mytable
		WHERE
			ID > 0
	)
);
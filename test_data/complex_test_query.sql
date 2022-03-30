CREATE assertion single_table_assertion CHECK (
    EXISTS (
        with temp(attrA, attrB) as (
            select
                *
            from
                (
                    with temp2(foo) as (
                        select
                            *
                        from
                            table1
                    )
                    select
                        *
                    from
                        temp2
                ) t1
                inner join (
                    select
                        *
                    from
                        table2 tt
                ) t2 on t1.attrC = t2.attrE + 5 << factorial(2)
            where
                t1.attrD = |/ 16 % 25
        )
        select
            *
        from
            table3 t3,
            table4
        where
            t3.attrG = table4.attrH
            and table4.attrI in (
                select
                    attrA
                from
                    temp
            )
    )
);
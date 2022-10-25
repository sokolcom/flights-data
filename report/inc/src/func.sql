\c db_delays;

CREATE OR REPLACE FUNCTION get_ac_operator(key_tailno VARCHAR(8))
    RETURNS TABLE(
        airline_id VARCHAR(2),
        fullname VARCHAR,
        tail_no VARCHAR(8),
        mfr VARCHAR,
        model VARCHAR,
        photo VARCHAR
    )
    LANGUAGE plpgsql
AS
$$
BEGIN
    RETURN QUERY
        SELECT DISTINCT al.airline_id, al.fullname, ac.tail_no, ac.mfr, ac.model, ac.photo
        FROM delays d JOIN aircrafts ac ON d.tail_no = ac.tail_no
            JOIN airlines al on d.airline_id = al.airline_id
        WHERE d.tail_no = key_tailno;
END;
$$;
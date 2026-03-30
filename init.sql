CREATE OR REPLACE FUNCTION SP_GET_CREDIT_DECISION(
    p_age NUMERIC,
    p_income NUMERIC,
    p_credit_history VARCHAR,
    p_employment VARCHAR
) RETURNS VARCHAR AS $$
BEGIN
    -- Validation block
    IF p_age IS NULL OR p_income IS NULL OR p_credit_history IS NULL OR p_employment IS NULL THEN
        RAISE EXCEPTION 'VALIDATION_ERROR: Null parameters are not allowed';
    END IF;

    IF p_age < 18 OR p_age > 100 THEN
        RAISE EXCEPTION 'VALIDATION_ERROR: Age out of bounds (18-100)';
    END IF;

    IF p_income < 0 OR p_income > 1000000 THEN
        RAISE EXCEPTION 'VALIDATION_ERROR: Income out of bounds (0-1000000)';
    END IF;

    IF p_credit_history NOT IN ('GOOD', 'BAD', 'EMPTY') THEN
        RAISE EXCEPTION 'VALIDATION_ERROR: Invalid credit history value';
    END IF;

    IF p_employment NOT IN ('EMPLOYED', 'UNEMPLOYED', 'SELF_EMPLOYED') THEN
        RAISE EXCEPTION 'VALIDATION_ERROR: Invalid employment value';
    END IF;

    -- Business logic Rule: BAD credit history -> always reject
    IF p_credit_history = 'BAD' THEN
        RETURN 'REJECT';
    END IF;

    -- Business logic Rule: UNEMPLOYED -> always reject
    IF p_employment = 'UNEMPLOYED' THEN
        RETURN 'REJECT';
    END IF;

    -- Business logic Rule: Age exception
    IF p_age < 21 THEN
        IF p_age >= 18 AND p_age <= 20 AND p_income > 50000 AND p_employment = 'EMPLOYED' THEN
            RETURN 'APPROVE';
        ELSE
            RETURN 'REJECT';
        END IF;
    END IF;

    -- Otherwise
    RETURN 'APPROVE';
END;
$$ LANGUAGE plpgsql;

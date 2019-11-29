CREATE USER donotban WITH PASSWORD 'donotbansilvousplait';

CREATE DATABASE donotban WITH OWNER donotban;

\c donotban

CREATE SEQUENCE book_id_seq AS integer;

ALTER SEQUENCE book_id_seq OWNER TO donotban;

CREATE TABLE book (
    id integer PRIMARY KEY NOT NULL DEFAULT nextval('book_id_seq'::regclass),
    title character varying(200) NOT NULL,
    subtitle character varying(200) NOT NULL DEFAULT ''::character varying,
    orig_title character varying(200) NOT NULL DEFAULT ''::character varying,
    author character varying(100)[] NOT NULL DEFAULT ARRAY[]::character varying[],
    translator character varying(100)[] NOT NULL DEFAULT ARRAY[]::character varying[],
    language character varying(10) NOT NULL DEFAULT ''::character varying,
    pub_house character varying(200) NOT NULL DEFAULT ''::character varying,
    pub_year integer,
    pub_month integer,
    binding character varying(50) NOT NULL DEFAULT ''::character varying,
    price character varying(50) NOT NULL DEFAULT ''::character varying,
    pages integer,
    isbn character varying(50) UNIQUE,
    other jsonb,
    img_url character varying(500) NOT NULL DEFAULT ''::character varying,
    rating numeric(2, 1),
    edited_time timestamp with time zone NOT NULL DEFAULT now(),
    is_deleted boolean NOT NULL DEFAULT false
);

ALTER TABLE book
    ADD CONSTRAINT book_pages_check CHECK (pages >= 0),
    ADD CONSTRAINT book_pub_month_lowerbound CHECK (pub_month >= 1),
    ADD CONSTRAINT book_pub_month_upperbound CHECK (pub_month <= 12),
    ADD CONSTRAINT book_pub_year_lowerbound CHECK (pub_year >= 0),
    ADD CONSTRAINT book_rating_lowerbound CHECK (rating >= 0::numeric),
    ADD CONSTRAINT book_rating_upperbound CHECK (rating <= 5::numeric),
    OWNER TO donotban;

GRANT CONNECT ON DATABASE donotban TO donotban;
GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON ALL TABLES IN SCHEMA public TO donotban;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO donotban;

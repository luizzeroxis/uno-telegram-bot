--
-- PostgreSQL database dump
--

-- Dumped from database version 13.3
-- Dumped by pg_dump version 13.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: uno_joins; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.uno_joins (
    id integer NOT NULL,
    room_id integer,
    user_id integer,
    player_number integer
);


--
-- Name: uno_joins_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.uno_joins_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: uno_joins_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.uno_joins_id_seq OWNED BY public.uno_joins.id;


--
-- Name: uno_rooms; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.uno_rooms (
    id integer NOT NULL,
    game_pickle bytea,
    draw_4_on_draw_4 text DEFAULT 'false'::text NOT NULL,
    draw_2_on_draw_4 text DEFAULT 'false'::text NOT NULL,
    disable_call_bluff text DEFAULT 'false'::text NOT NULL,
    allow_play_non_drawn_cards text DEFAULT 'false'::text NOT NULL,
    allow_pass_without_draw text DEFAULT 'false'::text NOT NULL,
    draw_pass_behavior text DEFAULT 'single_draw'::text NOT NULL,
    allow_highlight_playable_cards text DEFAULT 'false'::text NOT NULL,
    show_bluffer_cards text DEFAULT 'true'::text NOT NULL
);


--
-- Name: uno_rooms_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.uno_rooms_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: uno_rooms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.uno_rooms_id_seq OWNED BY public.uno_rooms.id;


--
-- Name: uno_users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.uno_users (
    id integer NOT NULL,
    user_id integer,
    style text DEFAULT 'short'::text NOT NULL,
    show_play_number text DEFAULT 'false'::text NOT NULL
);


--
-- Name: uno_users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.uno_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: uno_users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.uno_users_id_seq OWNED BY public.uno_users.id;


--
-- Name: uno_joins id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.uno_joins ALTER COLUMN id SET DEFAULT nextval('public.uno_joins_id_seq'::regclass);


--
-- Name: uno_rooms id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.uno_rooms ALTER COLUMN id SET DEFAULT nextval('public.uno_rooms_id_seq'::regclass);


--
-- Name: uno_users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.uno_users ALTER COLUMN id SET DEFAULT nextval('public.uno_users_id_seq'::regclass);


--
-- Name: uno_joins uno_joins_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.uno_joins
    ADD CONSTRAINT uno_joins_pkey PRIMARY KEY (id);


--
-- Name: uno_rooms uno_rooms_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.uno_rooms
    ADD CONSTRAINT uno_rooms_pkey PRIMARY KEY (id);


--
-- Name: uno_users uno_users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.uno_users
    ADD CONSTRAINT uno_users_pkey PRIMARY KEY (id);


--
-- Name: uno_users uq_uno_users_user_id; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.uno_users
    ADD CONSTRAINT uq_uno_users_user_id UNIQUE (user_id);


--
-- PostgreSQL database dump complete
--


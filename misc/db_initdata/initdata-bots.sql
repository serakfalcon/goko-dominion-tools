--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: bot; Type: TABLE; Schema: public; Owner: ai; Tablespace: 
--

CREATE TABLE bot (
    pname character varying(100) NOT NULL
);

--
-- Data for Name: bot; Type: TABLE DATA; Schema: public; Owner: ai
--

COPY bot (pname) FROM stdin;
Conqueror Bot
Lord Bottington
Banker Bot
Villager Bot
Village Idiot Bot
Serf Bot
Defender Bot
Warlord Bot
\.


--
-- Name: bot_pkey; Type: CONSTRAINT; Schema: public; Owner: ai; Tablespace: 
--

ALTER TABLE ONLY bot
    ADD CONSTRAINT bot_pkey PRIMARY KEY (pname);


--
-- PostgreSQL database dump complete
--


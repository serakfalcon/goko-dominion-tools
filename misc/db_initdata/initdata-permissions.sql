ALTER TABLE public.advbot OWNER TO ai;
ALTER TABLE public.bot OWNER TO ai;
REVOKE ALL ON TABLE bot FROM PUBLIC;
REVOKE ALL ON TABLE bot FROM ai;
GRANT ALL ON TABLE bot TO ai;
GRANT SELECT ON TABLE bot TO forum;
ALTER TABLE public.card_url OWNER TO ai;
REVOKE ALL ON TABLE card_url FROM PUBLIC;
REVOKE ALL ON TABLE card_url FROM ai;
GRANT ALL ON TABLE card_url TO ai;
GRANT SELECT ON TABLE card_url TO forum;

ALTER TABLE public.gain OWNER TO ai;
ALTER TABLE public.game OWNER TO ai;
ALTER TABLE public.old_rating OWNER TO ai;
ALTER TABLE public.phash OWNER TO ai;
ALTER TABLE public.presult OWNER TO ai;
ALTER TABLE public.ret OWNER TO ai;
ALTER TABLE public.temp_rcomp OWNER TO ai;
ALTER TABLE public.ts_rating OWNER TO ai;
ALTER TABLE public.ts_rating_history OWNER TO ai;
ALTER TABLE public.ts_rating_history_old OWNER TO ai;
ALTER TABLE public.ts_rating_old OWNER TO ai;
ALTER TABLE public.ts_state OWNER TO ai;
ALTER TABLE public.ts_system OWNER TO ai;
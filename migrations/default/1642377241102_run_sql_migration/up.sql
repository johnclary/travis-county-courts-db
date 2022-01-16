CREATE TRIGGER set_case_criminal_last_updated BEFORE UPDATE ON public.cases_criminal FOR EACH ROW EXECUTE FUNCTION public.set_last_updated();

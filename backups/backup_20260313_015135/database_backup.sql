--
-- PostgreSQL database dump
--

\restrict Xj4s22dthD4q82U4uXoVRVQXElYpkrfRWnLOfFxyU1bJYCw7ObHM2okRHZ2q12V

-- Dumped from database version 16.12 (6d3029c)
-- Dumped by pg_dump version 16.10

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
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO neondb_owner;

--
-- Name: appointment; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.appointment (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    doctor_id integer NOT NULL,
    start_time timestamp without time zone NOT NULL,
    end_time timestamp without time zone NOT NULL,
    status character varying(20),
    appointment_type character varying(20),
    notes text,
    waiting boolean,
    checked_in_time timestamp without time zone,
    room character varying(50),
    created_at timestamp without time zone,
    total_waiting_minutes integer,
    consultation_date timestamp without time zone
);


ALTER TABLE public.appointment OWNER TO neondb_owner;

--
-- Name: appointment_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.appointment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.appointment_id_seq OWNER TO neondb_owner;

--
-- Name: appointment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.appointment_id_seq OWNED BY public.appointment.id;


--
-- Name: attachment; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.attachment (
    id integer NOT NULL,
    doctor_id integer NOT NULL,
    doctor_patient_id integer,
    owner_type character varying(30),
    owner_id integer,
    file_path character varying(500),
    label character varying(200),
    created_at timestamp without time zone
);


ALTER TABLE public.attachment OWNER TO neondb_owner;

--
-- Name: attachment_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.attachment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.attachment_id_seq OWNER TO neondb_owner;

--
-- Name: attachment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.attachment_id_seq OWNED BY public.attachment.id;


--
-- Name: budget_cp; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.budget_cp (
    id integer NOT NULL,
    encounter_id integer NOT NULL,
    items json,
    all_in_price double precision,
    currency character varying(5)
);


ALTER TABLE public.budget_cp OWNER TO neondb_owner;

--
-- Name: budget_cp_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.budget_cp_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.budget_cp_id_seq OWNER TO neondb_owner;

--
-- Name: budget_cp_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.budget_cp_id_seq OWNED BY public.budget_cp.id;


--
-- Name: chat_message; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.chat_message (
    id integer NOT NULL,
    sender_id integer NOT NULL,
    recipient_id integer NOT NULL,
    message text NOT NULL,
    created_at timestamp without time zone,
    read boolean
);


ALTER TABLE public.chat_message OWNER TO neondb_owner;

--
-- Name: chat_message_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.chat_message_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.chat_message_id_seq OWNER TO neondb_owner;

--
-- Name: chat_message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.chat_message_id_seq OWNED BY public.chat_message.id;


--
-- Name: commercial_task; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.commercial_task (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    patient_name_snapshot character varying(100) NOT NULL,
    doctor_id integer NOT NULL,
    doctor_name_snapshot character varying(100) NOT NULL,
    consultation_id integer NOT NULL,
    source_type character varying(20) NOT NULL,
    planning_snapshot_json text NOT NULL,
    total_value numeric(10,2),
    status character varying(20) NOT NULL,
    priority character varying(20) NOT NULL,
    seller_notes text,
    next_followup_date date,
    last_contact_at timestamp without time zone,
    consultation_date date,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.commercial_task OWNER TO neondb_owner;

--
-- Name: commercial_task_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.commercial_task_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.commercial_task_id_seq OWNER TO neondb_owner;

--
-- Name: commercial_task_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.commercial_task_id_seq OWNED BY public.commercial_task.id;


--
-- Name: cosmetic_procedure_plan; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.cosmetic_procedure_plan (
    id integer NOT NULL,
    note_id integer NOT NULL,
    procedure_name character varying(100) NOT NULL,
    planned_value numeric(10,2),
    final_budget numeric(10,2),
    was_performed boolean,
    performed_date timestamp without time zone,
    follow_up_months integer,
    created_at timestamp without time zone,
    observations text DEFAULT ''::text
);


ALTER TABLE public.cosmetic_procedure_plan OWNER TO neondb_owner;

--
-- Name: cosmetic_procedure_plan_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.cosmetic_procedure_plan_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cosmetic_procedure_plan_id_seq OWNER TO neondb_owner;

--
-- Name: cosmetic_procedure_plan_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.cosmetic_procedure_plan_id_seq OWNED BY public.cosmetic_procedure_plan.id;


--
-- Name: doctor_preference; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.doctor_preference (
    id integer NOT NULL,
    user_id integer NOT NULL,
    color character varying(7),
    layer_enabled boolean,
    created_at timestamp without time zone
);


ALTER TABLE public.doctor_preference OWNER TO neondb_owner;

--
-- Name: doctor_preference_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.doctor_preference_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.doctor_preference_id_seq OWNER TO neondb_owner;

--
-- Name: doctor_preference_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.doctor_preference_id_seq OWNED BY public.doctor_preference.id;


--
-- Name: encounter_cp; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.encounter_cp (
    id integer NOT NULL,
    doctor_id integer NOT NULL,
    doctor_patient_id integer NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    category character varying(20),
    complaint_text text,
    plan_summary_text text,
    consultation_seconds integer,
    status character varying(10)
);


ALTER TABLE public.encounter_cp OWNER TO neondb_owner;

--
-- Name: encounter_cp_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.encounter_cp_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.encounter_cp_id_seq OWNER TO neondb_owner;

--
-- Name: encounter_cp_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.encounter_cp_id_seq OWNED BY public.encounter_cp.id;


--
-- Name: evolution; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.evolution (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    doctor_id integer NOT NULL,
    evolution_date timestamp without time zone NOT NULL,
    content text NOT NULL,
    created_at timestamp without time zone NOT NULL,
    consultation_id integer
);


ALTER TABLE public.evolution OWNER TO neondb_owner;

--
-- Name: evolution_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.evolution_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.evolution_id_seq OWNER TO neondb_owner;

--
-- Name: evolution_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.evolution_id_seq OWNED BY public.evolution.id;


--
-- Name: follow_up_reminder; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.follow_up_reminder (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    procedure_name character varying(100) NOT NULL,
    scheduled_date date NOT NULL,
    reminder_type character varying(50),
    status character varying(20),
    notes text,
    created_at timestamp without time zone
);


ALTER TABLE public.follow_up_reminder OWNER TO neondb_owner;

--
-- Name: follow_up_reminder_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.follow_up_reminder_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.follow_up_reminder_id_seq OWNER TO neondb_owner;

--
-- Name: follow_up_reminder_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.follow_up_reminder_id_seq OWNED BY public.follow_up_reminder.id;


--
-- Name: hair_transplant; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.hair_transplant (
    id integer NOT NULL,
    note_id integer NOT NULL,
    norwood_classification character varying(20),
    previous_transplant character varying(10),
    transplant_location character varying(50),
    case_type character varying(50),
    number_of_surgeries integer,
    body_hair_needed boolean,
    eyebrow_transplant boolean,
    beard_transplant boolean,
    frontal_transplant boolean,
    crown_transplant boolean,
    complete_transplant boolean,
    complete_with_body_hair boolean,
    surgical_planning text,
    clinical_conduct text,
    created_at timestamp without time zone,
    feminine_hair_transplant boolean DEFAULT false,
    dense_packing boolean DEFAULT false
);


ALTER TABLE public.hair_transplant OWNER TO neondb_owner;

--
-- Name: hair_transplant_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.hair_transplant_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.hair_transplant_id_seq OWNER TO neondb_owner;

--
-- Name: hair_transplant_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.hair_transplant_id_seq OWNED BY public.hair_transplant.id;


--
-- Name: indication; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.indication (
    id integer NOT NULL,
    note_id integer NOT NULL,
    procedure_id integer NOT NULL,
    indicated boolean,
    performed boolean,
    created_at timestamp without time zone
);


ALTER TABLE public.indication OWNER TO neondb_owner;

--
-- Name: indication_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.indication_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.indication_id_seq OWNER TO neondb_owner;

--
-- Name: indication_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.indication_id_seq OWNED BY public.indication.id;


--
-- Name: medication_usage; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.medication_usage (
    id integer NOT NULL,
    medication_id integer NOT NULL,
    prescribed_at timestamp without time zone
);


ALTER TABLE public.medication_usage OWNER TO neondb_owner;

--
-- Name: medication_usage_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.medication_usage_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.medication_usage_id_seq OWNER TO neondb_owner;

--
-- Name: medication_usage_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.medication_usage_id_seq OWNED BY public.medication_usage.id;


--
-- Name: medications; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.medications (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    purpose text,
    type character varying(50) NOT NULL,
    brand character varying(100),
    instructions text,
    created_at timestamp without time zone
);


ALTER TABLE public.medications OWNER TO neondb_owner;

--
-- Name: medications_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.medications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.medications_id_seq OWNER TO neondb_owner;

--
-- Name: medications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.medications_id_seq OWNED BY public.medications.id;


--
-- Name: message_read; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.message_read (
    id integer NOT NULL,
    message_id integer NOT NULL,
    user_id integer NOT NULL,
    read_at timestamp without time zone
);


ALTER TABLE public.message_read OWNER TO neondb_owner;

--
-- Name: message_read_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.message_read_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.message_read_id_seq OWNER TO neondb_owner;

--
-- Name: message_read_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.message_read_id_seq OWNED BY public.message_read.id;


--
-- Name: note; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.note (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    doctor_id integer NOT NULL,
    appointment_id integer,
    note_type character varying(50) NOT NULL,
    category character varying(50),
    content text,
    consultation_duration integer,
    created_at timestamp without time zone,
    transplant_indication character varying(10) DEFAULT 'nao'::character varying,
    surgical_planning text
);


ALTER TABLE public.note OWNER TO neondb_owner;

--
-- Name: note_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.note_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.note_id_seq OWNER TO neondb_owner;

--
-- Name: note_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.note_id_seq OWNED BY public.note.id;


--
-- Name: operating_room; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.operating_room (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    capacity integer,
    created_at timestamp without time zone
);


ALTER TABLE public.operating_room OWNER TO neondb_owner;

--
-- Name: operating_room_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.operating_room_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.operating_room_id_seq OWNER TO neondb_owner;

--
-- Name: operating_room_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.operating_room_id_seq OWNED BY public.operating_room.id;


--
-- Name: patient; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.patient (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    phone character varying(20),
    email character varying(120),
    birth_date date,
    cpf character varying(14),
    address character varying(200),
    patient_type character varying(50),
    attention_note text,
    created_at timestamp without time zone,
    city character varying(100),
    mother_name character varying(100),
    indication_source character varying(100),
    occupation character varying(100),
    state character varying(50),
    zip_code character varying(20),
    has_transplant_indication boolean DEFAULT false,
    photo_url character varying(255),
    ivp_stars integer,
    ivp_manual_override boolean DEFAULT false,
    ivp_updated_at timestamp without time zone,
    weight double precision,
    height double precision,
    blood_type character varying(5),
    allergies text,
    smoker character varying(20)
);


ALTER TABLE public.patient OWNER TO neondb_owner;

--
-- Name: patient_doctor; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.patient_doctor (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    doctor_id integer NOT NULL,
    patient_code integer NOT NULL,
    created_at timestamp without time zone
);


ALTER TABLE public.patient_doctor OWNER TO neondb_owner;

--
-- Name: patient_doctor_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.patient_doctor_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.patient_doctor_id_seq OWNER TO neondb_owner;

--
-- Name: patient_doctor_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.patient_doctor_id_seq OWNED BY public.patient_doctor.id;


--
-- Name: patient_funnel_status; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.patient_funnel_status (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    funnel_status character varying(100),
    funnel_temperature character varying(100),
    updated_at timestamp without time zone
);


ALTER TABLE public.patient_funnel_status OWNER TO neondb_owner;

--
-- Name: patient_funnel_status_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.patient_funnel_status_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.patient_funnel_status_id_seq OWNER TO neondb_owner;

--
-- Name: patient_funnel_status_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.patient_funnel_status_id_seq OWNED BY public.patient_funnel_status.id;


--
-- Name: patient_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.patient_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.patient_id_seq OWNER TO neondb_owner;

--
-- Name: patient_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.patient_id_seq OWNED BY public.patient.id;


--
-- Name: patient_tag; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.patient_tag (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    tag_id integer NOT NULL,
    created_at timestamp without time zone
);


ALTER TABLE public.patient_tag OWNER TO neondb_owner;

--
-- Name: patient_tag_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.patient_tag_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.patient_tag_id_seq OWNER TO neondb_owner;

--
-- Name: patient_tag_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.patient_tag_id_seq OWNED BY public.patient_tag.id;


--
-- Name: payment; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.payment (
    id integer NOT NULL,
    appointment_id integer,
    patient_id integer NOT NULL,
    total_amount numeric(10,2) NOT NULL,
    payment_method character varying(50) NOT NULL,
    installments integer,
    status character varying(20),
    procedures json,
    consultation_type character varying(50),
    created_at timestamp without time zone,
    paid_at timestamp without time zone
);


ALTER TABLE public.payment OWNER TO neondb_owner;

--
-- Name: payment_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.payment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.payment_id_seq OWNER TO neondb_owner;

--
-- Name: payment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.payment_id_seq OWNED BY public.payment.id;


--
-- Name: plan_cp; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.plan_cp (
    id integer NOT NULL,
    encounter_id integer NOT NULL,
    indication_status character varying(5),
    case_type character varying(20),
    selected_procedures json,
    lipo_areas json,
    implant_plane character varying(50),
    implant_profile character varying(50),
    implant_volume_min integer,
    implant_volume_max integer,
    technologies json,
    internacao character varying(20),
    estimated_time character varying(50),
    follow_up_deadline character varying(20),
    reception_obs text
);


ALTER TABLE public.plan_cp OWNER TO neondb_owner;

--
-- Name: plan_cp_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.plan_cp_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.plan_cp_id_seq OWNER TO neondb_owner;

--
-- Name: plan_cp_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.plan_cp_id_seq OWNED BY public.plan_cp.id;


--
-- Name: prescription; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.prescription (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    doctor_id integer NOT NULL,
    appointment_id integer,
    medications_oral json,
    medications_topical json,
    summary text,
    prescription_type character varying(50),
    created_at timestamp without time zone
);


ALTER TABLE public.prescription OWNER TO neondb_owner;

--
-- Name: prescription_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.prescription_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.prescription_id_seq OWNER TO neondb_owner;

--
-- Name: prescription_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.prescription_id_seq OWNED BY public.prescription.id;


--
-- Name: procedure; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.procedure (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    created_at timestamp without time zone
);


ALTER TABLE public.procedure OWNER TO neondb_owner;

--
-- Name: procedure_follow_up_rule; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.procedure_follow_up_rule (
    id integer NOT NULL,
    procedure_name character varying(100) NOT NULL,
    follow_up_months integer NOT NULL,
    description text,
    created_at timestamp without time zone
);


ALTER TABLE public.procedure_follow_up_rule OWNER TO neondb_owner;

--
-- Name: procedure_follow_up_rule_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.procedure_follow_up_rule_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.procedure_follow_up_rule_id_seq OWNER TO neondb_owner;

--
-- Name: procedure_follow_up_rule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.procedure_follow_up_rule_id_seq OWNED BY public.procedure_follow_up_rule.id;


--
-- Name: procedure_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.procedure_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.procedure_id_seq OWNER TO neondb_owner;

--
-- Name: procedure_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.procedure_id_seq OWNED BY public.procedure.id;


--
-- Name: procedure_record; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.procedure_record (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    doctor_id integer NOT NULL,
    procedure_name character varying(100) NOT NULL,
    status character varying(20),
    planned_date date,
    performed_date date,
    follow_up_due_at date,
    follow_up_status character varying(20),
    notes text,
    evolution_id integer,
    created_at timestamp without time zone
);


ALTER TABLE public.procedure_record OWNER TO neondb_owner;

--
-- Name: procedure_record_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.procedure_record_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.procedure_record_id_seq OWNER TO neondb_owner;

--
-- Name: procedure_record_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.procedure_record_id_seq OWNED BY public.procedure_record.id;


--
-- Name: surgery; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.surgery (
    id integer NOT NULL,
    date date NOT NULL,
    start_time time without time zone NOT NULL,
    end_time time without time zone NOT NULL,
    patient_id integer,
    patient_name character varying(100) NOT NULL,
    procedure_id integer,
    procedure_name character varying(200) NOT NULL,
    doctor_id integer NOT NULL,
    operating_room_id integer NOT NULL,
    status character varying(20),
    notes text,
    created_by integer NOT NULL,
    updated_by integer,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.surgery OWNER TO neondb_owner;

--
-- Name: surgery_evolution; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.surgery_evolution (
    id integer NOT NULL,
    surgery_id integer NOT NULL,
    doctor_id integer NOT NULL,
    evolution_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    content text NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    evolution_type character varying(20) DEFAULT 'general'::character varying,
    has_necrosis boolean DEFAULT false,
    has_scabs boolean DEFAULT false,
    has_infection boolean DEFAULT false,
    has_follicle_loss boolean DEFAULT false,
    result_rating character varying(20),
    needs_another_surgery boolean DEFAULT false,
    has_folliculitis_acute boolean DEFAULT false,
    has_folliculitis_chronic boolean DEFAULT false,
    has_rarefaction boolean DEFAULT false,
    has_local_failure boolean DEFAULT false,
    patient_satisfied boolean,
    result_within_expected boolean,
    using_oral_medication boolean,
    needs_body_hair boolean DEFAULT false,
    needs_touch_up boolean DEFAULT false
);


ALTER TABLE public.surgery_evolution OWNER TO neondb_owner;

--
-- Name: surgery_evolution_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.surgery_evolution_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.surgery_evolution_id_seq OWNER TO neondb_owner;

--
-- Name: surgery_evolution_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.surgery_evolution_id_seq OWNED BY public.surgery_evolution.id;


--
-- Name: surgery_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.surgery_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.surgery_id_seq OWNER TO neondb_owner;

--
-- Name: surgery_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.surgery_id_seq OWNED BY public.surgery.id;


--
-- Name: tag; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.tag (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    color character varying(7),
    created_at timestamp without time zone
);


ALTER TABLE public.tag OWNER TO neondb_owner;

--
-- Name: tag_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.tag_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tag_id_seq OWNER TO neondb_owner;

--
-- Name: tag_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.tag_id_seq OWNED BY public.tag.id;


--
-- Name: transplant_image; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.transplant_image (
    id integer NOT NULL,
    hair_transplant_id integer NOT NULL,
    image_type character varying(50) NOT NULL,
    file_path character varying(255) NOT NULL,
    description text,
    created_at timestamp without time zone
);


ALTER TABLE public.transplant_image OWNER TO neondb_owner;

--
-- Name: transplant_image_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.transplant_image_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.transplant_image_id_seq OWNER TO neondb_owner;

--
-- Name: transplant_image_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.transplant_image_id_seq OWNED BY public.transplant_image.id;


--
-- Name: transplant_surgery; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.transplant_surgery (
    id integer NOT NULL,
    hair_transplant_id integer NOT NULL,
    surgery_date timestamp without time zone NOT NULL,
    surgical_planning text,
    complications text,
    created_at timestamp without time zone
);


ALTER TABLE public.transplant_surgery OWNER TO neondb_owner;

--
-- Name: transplant_surgery_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.transplant_surgery_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.transplant_surgery_id_seq OWNER TO neondb_owner;

--
-- Name: transplant_surgery_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.transplant_surgery_id_seq OWNED BY public.transplant_surgery.id;


--
-- Name: transplant_surgery_record; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.transplant_surgery_record (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    doctor_id integer NOT NULL,
    surgery_date date NOT NULL,
    surgical_data text,
    observations text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    surgery_type character varying(200),
    status character varying(20) DEFAULT 'scheduled'::character varying,
    planning_snapshot text,
    calendar_event_id character varying(255)
);


ALTER TABLE public.transplant_surgery_record OWNER TO neondb_owner;

--
-- Name: transplant_surgery_record_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.transplant_surgery_record_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.transplant_surgery_record_id_seq OWNER TO neondb_owner;

--
-- Name: transplant_surgery_record_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.transplant_surgery_record_id_seq OWNED BY public.transplant_surgery_record.id;


--
-- Name: user; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public."user" (
    id integer NOT NULL,
    email character varying(120) NOT NULL,
    password_hash character varying(200) NOT NULL,
    name character varying(100) NOT NULL,
    role character varying(20) NOT NULL,
    specialty character varying(50),
    created_at timestamp without time zone,
    username character varying(50),
    role_clinico character varying(20) DEFAULT 'DERM'::character varying
);


ALTER TABLE public."user" OWNER TO neondb_owner;

--
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_id_seq OWNER TO neondb_owner;

--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- Name: appointment id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.appointment ALTER COLUMN id SET DEFAULT nextval('public.appointment_id_seq'::regclass);


--
-- Name: attachment id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.attachment ALTER COLUMN id SET DEFAULT nextval('public.attachment_id_seq'::regclass);


--
-- Name: budget_cp id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.budget_cp ALTER COLUMN id SET DEFAULT nextval('public.budget_cp_id_seq'::regclass);


--
-- Name: chat_message id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.chat_message ALTER COLUMN id SET DEFAULT nextval('public.chat_message_id_seq'::regclass);


--
-- Name: commercial_task id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.commercial_task ALTER COLUMN id SET DEFAULT nextval('public.commercial_task_id_seq'::regclass);


--
-- Name: cosmetic_procedure_plan id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.cosmetic_procedure_plan ALTER COLUMN id SET DEFAULT nextval('public.cosmetic_procedure_plan_id_seq'::regclass);


--
-- Name: doctor_preference id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.doctor_preference ALTER COLUMN id SET DEFAULT nextval('public.doctor_preference_id_seq'::regclass);


--
-- Name: encounter_cp id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.encounter_cp ALTER COLUMN id SET DEFAULT nextval('public.encounter_cp_id_seq'::regclass);


--
-- Name: evolution id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.evolution ALTER COLUMN id SET DEFAULT nextval('public.evolution_id_seq'::regclass);


--
-- Name: follow_up_reminder id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.follow_up_reminder ALTER COLUMN id SET DEFAULT nextval('public.follow_up_reminder_id_seq'::regclass);


--
-- Name: hair_transplant id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.hair_transplant ALTER COLUMN id SET DEFAULT nextval('public.hair_transplant_id_seq'::regclass);


--
-- Name: indication id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.indication ALTER COLUMN id SET DEFAULT nextval('public.indication_id_seq'::regclass);


--
-- Name: medication_usage id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.medication_usage ALTER COLUMN id SET DEFAULT nextval('public.medication_usage_id_seq'::regclass);


--
-- Name: medications id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.medications ALTER COLUMN id SET DEFAULT nextval('public.medications_id_seq'::regclass);


--
-- Name: message_read id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.message_read ALTER COLUMN id SET DEFAULT nextval('public.message_read_id_seq'::regclass);


--
-- Name: note id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.note ALTER COLUMN id SET DEFAULT nextval('public.note_id_seq'::regclass);


--
-- Name: operating_room id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.operating_room ALTER COLUMN id SET DEFAULT nextval('public.operating_room_id_seq'::regclass);


--
-- Name: patient id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.patient ALTER COLUMN id SET DEFAULT nextval('public.patient_id_seq'::regclass);


--
-- Name: patient_doctor id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.patient_doctor ALTER COLUMN id SET DEFAULT nextval('public.patient_doctor_id_seq'::regclass);


--
-- Name: patient_funnel_status id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.patient_funnel_status ALTER COLUMN id SET DEFAULT nextval('public.patient_funnel_status_id_seq'::regclass);


--
-- Name: patient_tag id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.patient_tag ALTER COLUMN id SET DEFAULT nextval('public.patient_tag_id_seq'::regclass);


--
-- Name: payment id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.payment ALTER COLUMN id SET DEFAULT nextval('public.payment_id_seq'::regclass);


--
-- Name: plan_cp id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.plan_cp ALTER COLUMN id SET DEFAULT nextval('public.plan_cp_id_seq'::regclass);


--
-- Name: prescription id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.prescription ALTER COLUMN id SET DEFAULT nextval('public.prescription_id_seq'::regclass);


--
-- Name: procedure id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.procedure ALTER COLUMN id SET DEFAULT nextval('public.procedure_id_seq'::regclass);


--
-- Name: procedure_follow_up_rule id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.procedure_follow_up_rule ALTER COLUMN id SET DEFAULT nextval('public.procedure_follow_up_rule_id_seq'::regclass);


--
-- Name: procedure_record id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.procedure_record ALTER COLUMN id SET DEFAULT nextval('public.procedure_record_id_seq'::regclass);


--
-- Name: surgery id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.surgery ALTER COLUMN id SET DEFAULT nextval('public.surgery_id_seq'::regclass);


--
-- Name: surgery_evolution id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.surgery_evolution ALTER COLUMN id SET DEFAULT nextval('public.surgery_evolution_id_seq'::regclass);


--
-- Name: tag id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.tag ALTER COLUMN id SET DEFAULT nextval('public.tag_id_seq'::regclass);


--
-- Name: transplant_image id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.transplant_image ALTER COLUMN id SET DEFAULT nextval('public.transplant_image_id_seq'::regclass);


--
-- Name: transplant_surgery id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.transplant_surgery ALTER COLUMN id SET DEFAULT nextval('public.transplant_surgery_id_seq'::regclass);


--
-- Name: transplant_surgery_record id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.transplant_surgery_record ALTER COLUMN id SET DEFAULT nextval('public.transplant_surgery_record_id_seq'::regclass);


--
-- Name: user id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.alembic_version (version_num) FROM stdin;
\.


--
-- Data for Name: appointment; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.appointment (id, patient_id, doctor_id, start_time, end_time, status, appointment_type, notes, waiting, checked_in_time, room, created_at, total_waiting_minutes, consultation_date) FROM stdin;
64	49	5	2025-12-09 13:15:00	2025-12-09 13:45:00	atendido	Botox	\N	f	2025-12-09 19:09:48.938713	\N	2025-12-09 18:18:15.202537	\N	\N
62	48	5	2025-12-09 13:30:00	2025-12-09 14:00:00	atendido	Infiltração Capilar	\N	f	2025-12-09 17:50:52.410508	\N	2025-12-09 17:50:41.559202	\N	\N
93	78	5	2025-12-12 18:15:00	2025-12-12 18:30:00	agendado	Retorno Botox	\N	f	\N	\N	2025-12-12 18:35:04.014672	\N	\N
65	50	5	2025-12-10 14:30:00	2025-12-10 15:30:00	atendido	Botox	\N	f	2025-12-10 17:09:07.337386	\N	2025-12-10 15:36:13.604374	\N	\N
70	55	5	2025-12-10 16:30:00	2025-12-10 17:00:00	faltou	Particular		f	\N	\N	2025-12-10 15:40:47.634768	\N	\N
71	56	5	2025-12-10 20:00:00	2025-12-10 20:30:00	agendado	Botox	\N	f	\N	\N	2025-12-10 15:41:58.879251	\N	\N
46	35	5	2025-12-04 15:00:00	2025-12-04 15:30:00	atendido	UNIMED		f	2025-12-04 18:08:19.722642	\N	2025-12-04 18:07:40.535373	\N	\N
73	58	5	2025-12-11 09:00:00	2025-12-11 09:30:00	atendido	UNIMED	saber sobre lipedema	f	2025-12-11 12:01:52.063113	\N	2025-12-11 11:52:16.140042	\N	\N
47	11	5	2025-12-04 16:00:00	2025-12-04 16:30:00	atendido	Transplante Capilar		t	2025-12-04 20:32:45.169975	\N	2025-12-04 19:21:24.779766	\N	\N
29	22	5	2025-12-02 11:00:00	2025-12-02 11:30:00	agendado	Retorno Botox	\N	f	\N	\N	2025-12-02 12:50:06.563319	\N	\N
30	23	5	2025-12-02 10:00:00	2025-12-02 10:30:00	agendado	Particular	\N	f	\N	\N	2025-12-02 12:50:22.217154	\N	\N
25	18	5	2025-12-02 08:00:00	2025-12-02 08:30:00	atendido	Particular	\N	f	2025-12-02 12:51:15.444565	\N	2025-12-02 12:35:21.928899	\N	\N
31	24	5	2025-12-02 14:30:00	2025-12-02 15:30:00	agendado	Particular		f	\N	\N	2025-12-02 12:52:02.435105	\N	\N
199	170	5	2026-02-03 16:00:00	2026-02-03 16:15:00	atendido	Particular		f	2026-02-03 19:53:48.117261	\N	2026-02-03 19:51:22.18345	\N	\N
95	80	5	2025-12-12 19:30:00	2025-12-12 19:40:00	agendado	Retorno 1 semana TX	\N	f	\N	\N	2025-12-12 18:42:30.595549	\N	\N
75	60	5	2025-12-11 17:00:00	2025-12-11 17:30:00	atendido	UNIMED	\N	f	2025-12-11 13:28:21.723062	\N	2025-12-11 13:28:09.749371	\N	\N
1	1	5	2025-11-25 13:30:00	2025-11-25 14:00:00	agendado	Botox		f	\N	\N	2025-11-25 18:00:29.886802	\N	\N
78	63	5	2025-12-11 14:00:00	2025-12-11 14:15:00	atendido	Particular	\N	f	2025-12-11 17:59:53.992366	\N	2025-12-11 17:57:52.689502	\N	\N
26	19	5	2025-12-02 09:00:00	2025-12-02 09:30:00	atendido	UNIMED	\N	f	2025-12-02 13:03:32.113901	\N	2025-12-02 12:39:53.632508	\N	\N
33	26	5	2025-12-02 17:30:00	2025-12-02 18:00:00	agendado	UNIMED	\N	f	\N	\N	2025-12-02 13:00:39.145619	\N	\N
80	65	5	2025-12-11 15:15:00	2025-12-11 15:45:00	atendido	Particular	\N	f	2025-12-11 19:19:03.241935	\N	2025-12-11 19:07:40.066254	\N	\N
97	81	5	2025-12-12 16:00:00	2025-12-12 16:15:00	atendido	Botox	\N	f	2025-12-12 19:49:35.729796	\N	2025-12-12 19:49:20.589183	\N	\N
84	69	5	2025-12-12 14:00:00	2025-12-12 14:30:00	agendado	Retirada de Ponto	\N	f	\N	\N	2025-12-12 12:29:36.458099	\N	\N
90	75	5	2025-12-12 07:30:00	2025-12-12 07:45:00	atendido	Cirurgia	\N	f	2025-12-12 18:10:12.191631	\N	2025-12-12 18:08:20.78741	\N	\N
81	66	5	2025-12-12 09:00:00	2025-12-12 09:30:00	atendido	Particular	\N	f	2025-12-12 12:26:17.261666	\N	2025-12-12 12:25:14.460765	\N	\N
3	3	6	2025-11-25 15:30:00	2025-11-25 16:30:00	agendado	Transplante Capilar	RETORNO DE 1 SEMANA DE IMPLANTE 	f	\N	\N	2025-11-25 18:34:27.040367	\N	\N
87	72	5	2025-12-12 14:00:00	2025-12-12 14:30:00	atendido	Retorno Botox	\N	f	2025-12-12 14:08:57.901802	\N	2025-12-12 12:40:44.794966	\N	\N
114	96	5	2025-12-16 14:30:00	2025-12-16 14:45:00	agendado	Botox	MORA SINGAPURA	f	\N	\N	2025-12-16 13:27:25.403506	\N	\N
112	94	5	2025-12-16 09:00:00	2025-12-16 09:15:00	atendido	Botox	\N	f	2025-12-16 13:25:32.917661	\N	2025-12-16 13:23:12.457807	\N	\N
101	84	5	2025-12-15 13:00:00	2025-12-15 13:15:00	atendido	Botox	\N	f	2025-12-15 13:01:08.902634	\N	2025-12-15 13:00:23.330264	\N	\N
105	87	5	2025-12-15 13:30:00	2025-12-15 13:45:00	agendado	Retorno Botox	\N	f	\N	\N	2025-12-15 13:25:06.268508	\N	\N
106	88	5	2025-12-15 14:00:00	2025-12-15 14:15:00	agendado	Retorno Botox	\N	f	\N	\N	2025-12-15 13:28:54.980364	\N	\N
109	91	5	2025-12-15 15:30:00	2025-12-15 15:45:00	agendado	Transplante Capilar	\N	f	\N	\N	2025-12-15 13:34:13.041898	\N	\N
4	4	6	2025-11-25 17:00:00	2025-11-25 17:30:00	agendado	Preenchimento	SCUPTRA	f	\N	\N	2025-11-25 18:35:44.289986	\N	\N
2	2	5	2025-11-25 15:30:00	2025-11-25 16:30:00	atendido	Particular		f	2025-11-25 18:52:41.044521	\N	2025-11-25 18:11:56.750361	\N	\N
5	5	6	2025-11-26 09:00:00	2025-11-26 09:30:00	agendado	Retorno Botox	\N	f	\N	\N	2025-11-26 11:39:29.172738	\N	\N
6	6	6	2025-11-26 09:45:00	2025-11-26 10:15:00	agendado	Transplante Capilar		f	\N	\N	2025-11-26 12:42:25.403872	\N	\N
8	8	6	2025-11-26 13:00:00	2025-11-26 13:30:00	agendado	Transplante Capilar	CIRURGIA DE IMPLANTE CAPILAR 	f	\N	\N	2025-11-26 12:44:20.771738	\N	\N
9	9	6	2025-11-26 09:00:00	2025-11-26 09:30:00	agendado	UNIMED	\N	f	\N	\N	2025-11-26 12:45:43.389421	\N	\N
10	10	5	2025-11-26 14:00:00	2025-11-26 14:30:00	agendado	Transplante Capilar	\N	f	\N	\N	2025-11-26 18:01:37.686571	\N	\N
27	20	5	2025-12-02 10:00:00	2025-12-02 10:30:00	agendado	Transplante Capilar		f	2025-12-02 13:21:53.480332	\N	2025-12-02 12:47:01.591146	\N	\N
14	13	6	2025-11-27 14:00:00	2025-11-27 14:30:00	agendado	UNIMED	\N	f	\N	\N	2025-11-27 17:19:46.194752	\N	\N
15	14	6	2025-11-27 15:00:00	2025-11-27 15:30:00	agendado	Transplante Capilar	\N	f	\N	\N	2025-11-27 17:20:34.949127	\N	\N
16	13	5	2025-11-27 15:00:00	2025-11-27 15:30:00	agendado	UNIMED	\N	f	\N	\N	2025-11-27 17:57:45.350399	\N	\N
17	14	5	2025-11-27 16:00:00	2025-11-27 16:30:00	agendado	Transplante Capilar	\N	f	\N	\N	2025-11-27 17:58:57.276292	\N	\N
28	21	5	2025-12-02 12:00:00	2025-12-02 12:30:00	atendido	Retorno Botox	\N	f	2025-12-02 14:01:24.912839	\N	2025-12-02 12:48:37.089314	\N	\N
13	1	5	2025-11-27 13:00:00	2025-11-27 13:30:00	atendido	Botox	\N	f	2025-11-27 23:02:34.459482	\N	2025-11-27 16:52:09.593706	\N	\N
19	15	5	2025-11-28 09:00:00	2025-11-28 09:30:00	agendado	Retorno	\N	f	\N	\N	2025-11-28 12:33:12.974938	\N	\N
32	25	5	2025-12-02 13:30:00	2025-12-02 14:00:00	atendido	Particular		f	2025-12-02 19:30:47.44911	\N	2025-12-02 12:53:49.573764	\N	\N
21	16	5	2025-11-28 14:00:00	2025-11-28 14:30:00	agendado	Laser	FEITO NO CENTRO CIRURGICO	f	\N	\N	2025-11-28 15:56:09.691303	\N	\N
34	27	5	2025-12-03 09:00:00	2025-12-03 09:30:00	agendado	UNIMED	\N	f	\N	\N	2025-12-03 12:27:10.223594	\N	\N
22	17	5	2025-11-28 16:00:00	2025-11-28 16:30:00	atendido	Botox	\N	f	2025-11-28 19:52:12.653981	\N	2025-11-28 19:51:20.168157	\N	\N
111	93	5	2025-12-15 16:00:00	2025-12-15 16:15:00	agendado	Particular	\N	f	\N	\N	2025-12-15 13:38:20.459291	\N	\N
99	82	5	2025-12-15 09:00:00	2025-12-15 09:15:00	atendido	Retorno Botox	\N	f	2025-12-15 12:54:35.750474	\N	2025-12-15 12:53:26.897958	\N	\N
107	89	5	2025-12-15 14:30:00	2025-12-15 14:45:00	atendido	Retorno 1 semana TX	\N	f	2025-12-15 18:34:51.245349	\N	2025-12-15 13:31:29.888597	\N	\N
103	86	5	2025-12-15 10:30:00	2025-12-15 10:45:00	atendido	Retorno Botox	\N	f	2025-12-15 18:58:15.48601	\N	2025-12-15 13:10:12.969226	\N	\N
110	92	5	2025-12-15 16:30:00	2025-12-15 16:45:00	atendido	Botox	\N	f	2025-12-15 20:03:59.963741	\N	2025-12-15 13:35:47.229819	\N	\N
121	99	5	2026-01-19 15:00:00	2026-01-19 15:15:00	atendido	Retorno Botox	\N	f	2026-01-19 18:37:15.533494	\N	2026-01-19 17:24:07.061046	\N	\N
115	48	5	2025-12-17 08:30:00	2025-12-17 08:45:00	atendido	Preenchimento	\N	f	2025-12-17 12:02:32.283126	\N	2025-12-17 12:02:15.593875	\N	\N
116	1	5	2025-12-24 08:00:00	2025-12-24 08:15:00	agendado	Ulthera	\N	f	\N	\N	2025-12-25 00:51:44.981725	\N	\N
117	97	5	2026-01-19 14:00:00	2026-01-19 14:15:00	agendado	Retorno Botox	\N	f	\N	\N	2026-01-19 15:36:28.356003	\N	\N
119	98	5	2026-01-19 17:30:00	2026-01-19 17:45:00	atendido	Retorno Botox	\N	f	2026-01-19 17:19:36.870834	\N	2026-01-19 17:16:54.089231	\N	\N
126	103	5	2026-01-21 11:00:00	2026-01-21 11:15:00	atendido	Retorno Botox	\N	f	2026-01-21 14:01:24.909727	\N	2026-01-21 13:09:54.933694	\N	\N
132	107	5	2026-01-21 15:30:00	2026-01-21 15:45:00	atendido	Transplante Capilar	\N	f	2026-01-21 18:23:54.880142	\N	2026-01-21 14:48:38.941736	\N	\N
131	106	5	2026-01-21 15:15:00	2026-01-21 15:30:00	agendado	Transplante Capilar	\N	f	\N	\N	2026-01-21 14:47:56.502859	\N	\N
123	70	5	2026-01-21 10:00:00	2026-01-21 10:15:00	atendido	Retorno Botox	\N	f	2026-01-21 12:58:26.433025	\N	2026-01-21 12:58:03.070098	\N	\N
130	96	5	2026-01-21 15:00:00	2026-01-21 15:15:00	atendido	Retorno Botox	\N	f	2026-01-21 20:16:32.833918	\N	2026-01-21 14:47:26.817959	\N	\N
129	105	5	2026-01-21 14:30:00	2026-01-21 14:45:00	atendido	Particular	\N	f	2026-01-21 18:10:14.263497	\N	2026-01-21 14:46:46.810027	\N	\N
140	115	5	2026-01-22 10:00:00	2026-01-22 10:15:00	atendido	UNIMED	\N	f	2026-01-22 12:53:33.782053	\N	2026-01-22 12:52:54.894247	\N	\N
138	113	5	2026-01-22 09:00:00	2026-01-22 09:15:00	atendido	UNIMED	\N	f	2026-01-22 12:15:03.963779	\N	2026-01-22 12:13:21.545347	\N	\N
141	116	5	2026-01-22 10:30:00	2026-01-22 10:45:00	atendido	UNIMED	\N	f	2026-01-22 14:12:27.65176	\N	2026-01-22 14:11:19.302577	\N	\N
143	117	5	2026-01-22 17:30:00	2026-01-22 17:45:00	agendado	Retorno Botox	\N	f	\N	\N	2026-01-22 14:23:53.585737	\N	\N
145	119	5	2026-01-23 14:30:00	2026-01-23 14:45:00	agendado	UNIMED		f	\N	\N	2026-01-23 17:28:42.329171	\N	\N
35	7	5	2025-12-03 09:00:00	2025-12-03 09:30:00	agendado	Particular	RETORNO DE PONTO	f	\N	\N	2025-12-03 12:27:59.213971	\N	\N
23	11	5	2025-11-27 17:00:00	2025-11-27 17:30:00	agendado	Particular	\N	f	\N	\N	2025-12-02 02:44:50.22089	\N	\N
24	18	6	2025-12-02 09:00:00	2025-12-02 09:30:00	agendado	UNIMED	\N	f	\N	\N	2025-12-02 12:34:35.022027	\N	\N
37	29	6	2025-12-03 10:00:00	2025-12-03 10:30:00	agendado	UNIMED	\N	f	\N	\N	2025-12-03 12:33:41.435587	\N	\N
38	29	5	2025-12-03 10:00:00	2025-12-03 10:30:00	agendado	UNIMED	\N	f	\N	\N	2025-12-03 12:34:42.397325	\N	\N
40	31	6	2025-12-03 14:00:00	2025-12-03 14:30:00	agendado	Botox	\N	f	\N	\N	2025-12-03 12:40:49.897449	\N	\N
41	31	6	2025-12-03 11:00:00	2025-12-03 11:30:00	agendado	Particular	\N	f	\N	\N	2025-12-03 12:41:30.465328	\N	\N
43	32	5	2025-12-03 07:00:00	2025-12-03 07:30:00	agendado	Transplante Capilar	\N	f	\N	\N	2025-12-03 12:43:55.951112	\N	\N
42	31	5	2025-12-03 11:00:00	2025-12-03 11:30:00	faltou	Particular	\N	f	\N	\N	2025-12-03 12:41:59.148859	\N	\N
44	33	5	2025-12-03 14:00:00	2025-12-03 14:30:00	atendido	Botox	\N	f	2025-12-03 18:47:43.943709	\N	2025-12-03 18:25:58.348676	\N	\N
39	30	5	2025-12-03 10:00:00	2025-12-03 10:30:00	atendido	Transplante Capilar	\N	f	2025-12-03 20:06:06.011993	\N	2025-12-03 12:37:03.731869	\N	\N
36	28	5	2025-12-03 09:15:00	2025-12-03 09:30:00	atendido	Particular		f	2025-12-03 20:10:52.243357	\N	2025-12-03 12:29:53.713061	\N	\N
45	34	5	2025-12-04 11:30:00	2025-12-04 12:00:00	atendido	Retorno Botox	\N	f	2025-12-04 15:32:09.893584	\N	2025-12-04 13:48:50.13361	\N	\N
61	47	5	2025-12-09 14:00:00	2025-12-09 14:30:00	atendido	Botox	\N	f	2025-12-09 17:46:03.485508	\N	2025-12-09 15:35:21.631712	\N	\N
60	46	5	2025-12-09 14:30:00	2025-12-09 15:00:00	atendido	Botox	\N	f	2025-12-09 17:46:06.386718	\N	2025-12-09 15:34:59.06346	\N	\N
104	80	5	2025-12-15 11:00:00	2025-12-15 11:15:00	atendido	Transplante Capilar	\N	f	2025-12-15 13:15:42.096298	\N	2025-12-15 13:12:20.599136	\N	\N
56	42	5	2025-12-09 16:30:00	2025-12-09 17:00:00	atendido	Particular		f	2025-12-09 20:31:49.051516	\N	2025-12-09 15:30:37.296243	\N	\N
82	67	5	2025-12-12 09:15:00	2025-12-12 09:45:00	atendido	Retorno Botox	\N	f	2025-12-12 12:31:28.379875	\N	2025-12-12 12:26:54.489275	\N	\N
48	1	5	2025-12-04 08:00:00	2025-12-04 08:30:00	atendido	Particular	\N	t	2025-12-04 20:32:50.356523	\N	2025-12-04 20:03:41.512364	\N	\N
58	44	5	2025-12-09 15:30:00	2025-12-09 16:00:00	atendido	Transplante Capilar	\N	f	2025-12-09 19:15:48.943115	\N	2025-12-09 15:33:49.783544	\N	\N
57	43	5	2025-12-09 16:00:00	2025-12-09 16:30:00	atendido	Preenchimento	\N	f	2025-12-09 19:16:02.131252	\N	2025-12-09 15:32:36.685942	\N	\N
55	41	5	2025-12-09 17:00:00	2025-12-09 17:30:00	atendido	Particular		f	2025-12-09 20:33:20.229925	\N	2025-12-09 15:29:38.236812	\N	\N
59	45	5	2025-12-09 15:00:00	2025-12-09 15:30:00	faltou	UNIMED	\N	f	\N	\N	2025-12-09 15:34:12.081811	\N	\N
66	51	5	2025-12-10 14:45:00	2025-12-10 15:15:00	atendido	UNIMED	\N	f	2025-12-10 17:29:29.65642	\N	2025-12-10 15:37:13.972786	\N	\N
67	52	5	2025-12-10 15:00:00	2025-12-10 15:30:00	atendido	Transplante Capilar	\N	f	2025-12-10 18:06:10.607025	\N	2025-12-10 15:38:44.791759	\N	\N
72	57	5	2025-12-10 15:30:00	2025-12-10 16:00:00	atendido	Transplante Capilar	\N	f	2025-12-10 18:13:11.191257	\N	2025-12-10 18:11:18.147031	\N	\N
69	54	5	2025-12-10 16:00:00	2025-12-10 16:30:00	atendido	Botox	\N	f	2025-12-10 19:57:00.872482	\N	2025-12-10 15:40:21.236153	\N	\N
128	104	5	2026-01-21 11:30:00	2026-01-21 11:45:00	atendido	Botox	\N	f	2026-01-21 14:29:26.303071	\N	2026-01-21 14:19:36.534488	\N	\N
74	59	5	2025-12-11 09:30:00	2025-12-11 10:00:00	atendido	Retorno Botox	\N	f	2025-12-11 12:34:57.281365	\N	2025-12-11 11:55:24.511016	\N	\N
50	37	5	2025-12-05 09:15:00	2025-12-05 09:45:00	atendido	Retorno Botox	\N	f	2025-12-05 12:48:34.323583	\N	2025-12-05 12:48:25.690226	\N	\N
49	36	5	2025-12-05 17:00:00	2025-12-05 17:30:00	atendido	Particular	\N	f	2025-12-05 12:48:50.374497	\N	2025-12-05 12:47:41.793075	\N	\N
52	39	5	2025-12-05 17:30:00	2025-12-05 18:00:00	atendido	Transplante Capilar	\N	f	2025-12-05 13:16:35.691646	\N	2025-12-05 13:16:17.529014	\N	\N
51	38	5	2025-12-05 14:00:00	2025-12-05 14:30:00	atendido	Transplante Capilar	\N	f	2025-12-05 12:55:44.575669	\N	2025-12-05 12:52:27.637137	\N	\N
53	40	5	2025-12-05 16:30:00	2025-12-05 17:00:00	agendado	Retorno Botox	\N	f	\N	\N	2025-12-05 17:44:38.829197	\N	\N
54	40	5	2025-12-05 16:30:00	2025-12-05 17:00:00	agendado	Retorno Botox	\N	f	\N	\N	2025-12-05 17:44:39.450957	\N	\N
83	68	5	2025-12-12 16:30:00	2025-12-12 17:00:00	faltou	Particular	\N	f	\N	\N	2025-12-12 12:27:55.120416	\N	\N
91	76	5	2025-12-12 14:30:00	2025-12-12 14:45:00	agendado	Transplante Capilar	\N	f	\N	\N	2025-12-12 18:33:52.035055	\N	\N
113	95	5	2025-12-16 09:30:00	2025-12-16 09:45:00	atendido	Botox	\N	f	2025-12-16 13:27:34.539067	\N	2025-12-16 13:25:30.566902	\N	\N
76	61	5	2025-12-11 10:45:00	2025-12-11 11:15:00	atendido	Particular	\N	f	2025-12-11 14:53:51.97832	\N	2025-12-11 13:37:59.320489	\N	\N
77	62	5	2025-12-11 11:15:00	2025-12-11 11:45:00	atendido	Botox	\N	f	2025-12-11 14:53:54.671658	\N	2025-12-11 14:53:38.538249	\N	\N
79	64	5	2025-12-11 14:30:00	2025-12-11 15:00:00	atendido	Particular	\N	f	2025-12-11 18:15:29.624411	\N	2025-12-11 18:15:15.952453	\N	\N
94	79	5	2025-12-12 18:30:00	2025-12-12 18:40:00	agendado	Retorno Botox	\N	f	\N	\N	2025-12-12 18:40:00.01223	\N	\N
86	71	5	2025-12-12 17:30:00	2025-12-12 17:40:00	agendado	Retorno Botox	\N	f	\N	\N	2025-12-12 12:37:10.653878	\N	\N
92	77	5	2025-12-12 15:00:00	2025-12-12 15:15:00	atendido	Retorno Botox	\N	f	2025-12-12 18:35:28.769909	\N	2025-12-12 18:34:33.12781	\N	\N
96	78	5	2025-12-12 15:30:00	2025-12-12 15:45:00	atendido	Particular	\N	f	2025-12-12 18:45:59.274673	\N	2025-12-12 18:45:43.206029	\N	\N
89	74	5	2025-12-12 17:00:00	2025-12-12 17:15:00	atendido	Particular	\N	f	2025-12-12 12:58:23.749239	\N	2025-12-12 12:45:22.344218	\N	\N
88	73	5	2025-12-12 18:30:00	2025-12-12 19:00:00	atendido	Particular	\N	f	2025-12-12 13:15:41.343716	\N	2025-12-12 12:42:01.436772	\N	\N
85	70	5	2025-12-12 18:00:00	2025-12-12 18:30:00	atendido	Botox	\N	f	2025-12-12 12:31:25.744352	\N	2025-12-12 12:30:39.523151	\N	\N
98	1	5	2025-12-12 11:00:00	2025-12-12 11:15:00	atendido	Particular	\N	f	2025-12-12 20:17:35.549896	\N	2025-12-12 20:15:31.043494	\N	\N
135	110	5	2026-01-21 17:00:00	2026-01-21 17:15:00	agendado	Botox	\N	f	\N	\N	2026-01-21 14:51:04.281376	\N	\N
100	83	5	2025-12-15 09:30:00	2025-12-15 09:45:00	atendido	Botox	\N	f	2025-12-15 12:59:03.383865	\N	2025-12-15 12:54:51.132854	\N	\N
108	90	5	2025-12-15 15:00:00	2025-12-15 15:15:00	agendado	Retorno Botox	\N	f	\N	\N	2025-12-15 13:33:31.731873	\N	\N
102	85	5	2025-12-15 10:00:00	2025-12-15 10:15:00	atendido	Particular	\N	f	2025-12-15 13:08:26.382803	\N	2025-12-15 13:02:28.343376	\N	\N
120	54	5	2026-01-19 15:30:00	2026-01-19 15:45:00	atendido	Retorno Botox	\N	f	2026-01-19 17:21:48.855321	\N	2026-01-19 17:20:09.364983	\N	\N
122	100	5	2026-01-19 16:00:00	2026-01-19 16:15:00	atendido	Botox	\N	f	2026-01-19 17:36:48.519922	\N	2026-01-19 17:36:24.056183	\N	\N
118	63	5	2026-01-19 14:15:00	2026-01-19 14:30:00	atendido	Retorno Botox	\N	f	2026-01-19 18:45:47.974272	\N	2026-01-19 17:15:09.040224	\N	\N
133	108	5	2026-01-21 16:00:00	2026-01-21 16:15:00	atendido	Infiltração Capilar	\N	f	2026-01-21 19:44:43.51559	\N	2026-01-21 14:49:10.745896	\N	\N
134	109	5	2026-01-21 16:30:00	2026-01-21 16:45:00	atendido	Retorno Botox	\N	f	2026-01-21 19:44:45.228786	\N	2026-01-21 14:49:37.144097	\N	\N
136	111	5	2026-01-21 17:15:00	2026-01-21 17:30:00	atendido	Retorno Botox	\N	f	2026-01-21 19:57:39.311982	\N	2026-01-21 14:51:30.133367	\N	\N
137	112	5	2026-01-21 17:30:00	2026-01-21 17:45:00	agendado	Botox	\N	f	\N	\N	2026-01-21 14:51:49.673795	\N	\N
124	101	5	2026-01-21 09:30:00	2026-01-21 09:45:00	atendido	UNIMED	\N	f	2026-01-21 13:09:21.966434	\N	2026-01-21 13:00:05.624622	\N	\N
125	102	5	2026-01-21 10:30:00	2026-01-21 10:45:00	atendido	Transplante Capilar	\N	f	2026-01-21 13:32:30.901009	\N	2026-01-21 13:08:17.949172	\N	\N
142	97	5	2026-01-22 11:00:00	2026-01-22 11:15:00	atendido	Retorno Botox	\N	f	2026-01-22 14:12:27.161725	\N	2026-01-22 14:11:40.569564	\N	\N
144	118	5	2026-01-22 14:45:00	2026-01-22 15:00:00	agendado	Transplante Capilar	\N	f	\N	\N	2026-01-22 14:25:48.664107	\N	\N
139	114	5	2026-01-22 09:15:00	2026-01-22 09:30:00	atendido	UNIMED	\N	f	2026-01-22 12:51:43.785466	\N	2026-01-22 12:25:09.127725	\N	\N
147	121	5	2026-01-23 16:00:00	2026-01-23 16:15:00	atendido	Retorno Botox		f	2026-01-23 19:17:17.647127	\N	2026-01-23 17:43:16.018182	\N	\N
146	120	5	2026-01-23 15:30:00	2026-01-23 15:45:00	atendido	Transplante Capilar		f	2026-01-23 18:15:37.529518	\N	2026-01-23 17:30:07.081701	\N	\N
149	123	5	2026-01-23 16:30:00	2026-01-23 16:45:00	atendido	Laser		f	2026-01-23 19:17:18.129493	\N	2026-01-23 17:45:07.453941	\N	\N
148	122	5	2026-01-23 15:45:00	2026-01-23 16:00:00	atendido	Retorno Botox		f	2026-01-23 18:52:12.880154	\N	2026-01-23 17:44:04.964934	\N	\N
151	125	5	2026-01-26 14:30:00	2026-01-26 14:45:00	agendado	UNIMED		f	\N	\N	2026-01-26 17:35:19.201706	\N	\N
153	127	5	2026-01-26 15:30:00	2026-01-26 15:45:00	agendado	Botox		f	\N	\N	2026-01-26 17:43:51.993547	\N	\N
155	129	5	2026-01-26 16:30:00	2026-01-26 16:45:00	agendado	Transplante Capilar		f	\N	\N	2026-01-26 17:46:09.730526	\N	\N
157	74	5	2026-01-27 09:00:00	2026-01-27 09:15:00	atendido	Botox		f	2026-01-27 12:00:29.503669	\N	2026-01-26 18:14:56.770155	\N	\N
150	124	5	2026-01-26 11:00:00	2026-01-26 11:15:00	atendido	Botox		f	2026-01-26 18:18:55.979473	\N	2026-01-26 17:34:33.921042	\N	\N
169	142	5	2026-01-27 15:30:00	2026-01-27 15:45:00	agendado	Transplante Capilar		f	\N	\N	2026-01-26 18:31:26.809147	\N	\N
170	143	5	2026-01-27 16:00:00	2026-01-27 16:15:00	agendado	Botox		f	\N	\N	2026-01-26 18:34:52.960727	\N	\N
154	128	5	2026-01-26 16:00:00	2026-01-26 16:15:00	atendido	Botox		f	2026-01-26 19:07:30.700943	\N	2026-01-26 17:44:52.299893	\N	\N
158	131	5	2026-01-27 09:30:00	2026-01-27 09:45:00	atendido	Transplante Capilar		f	2026-01-27 11:55:20.529663	\N	2026-01-26 18:15:23.689525	\N	\N
253	221	5	2026-02-11 15:30:00	2026-02-11 15:45:00	faltou	Botox		f	\N	\N	2026-02-11 12:10:29.907882	\N	\N
160	133	5	2026-01-27 10:30:00	2026-01-27 10:45:00	atendido	Retorno		f	2026-01-27 13:19:15.145514	\N	2026-01-26 18:17:04.940228	\N	\N
163	136	5	2026-01-27 11:00:00	2026-01-27 11:15:00	atendido	Retorno Botox		f	2026-01-27 13:30:13.227306	\N	2026-01-26 18:27:56.067741	\N	\N
202	173	5	2026-02-04 10:00:00	2026-02-04 10:15:00	atendido	Botox		f	2026-02-04 13:45:08.278052	\N	2026-02-04 11:54:46.904029	\N	\N
204	175	5	2026-02-04 11:00:00	2026-02-04 11:15:00	atendido	Botox		f	2026-02-04 14:00:03.023358	\N	2026-02-04 12:00:19.454979	\N	\N
256	224	5	2026-02-11 17:20:00	2026-02-11 17:35:00	agendado	Particular		t	2026-02-11 20:17:08.460783	\N	2026-02-11 12:11:56.108108	\N	\N
210	181	5	2026-02-05 14:30:00	2026-02-05 14:45:00	atendido	UNIMED		f	2026-02-05 17:08:22.921163	\N	2026-02-05 12:18:46.378007	\N	\N
208	179	5	2026-02-05 10:00:00	2026-02-05 10:15:00	atendido	Transplante Capilar		f	2026-02-05 13:06:15.877849	\N	2026-02-05 12:17:46.535281	\N	\N
215	186	5	2026-02-05 16:15:00	2026-02-05 16:30:00	faltou	UNIMED		f	\N	\N	2026-02-05 12:21:59.447465	\N	\N
222	135	5	2026-02-06 10:15:00	2026-02-06 10:30:00	atendido	Transplante Capilar		f	2026-02-06 13:10:48.960399	\N	2026-02-06 11:36:05.09691	\N	\N
260	228	5	2026-02-12 09:30:00	2026-02-12 09:45:00	atendido	Particular		f	2026-02-12 11:53:22.115661	\N	2026-02-11 20:35:00.703346	\N	\N
230	198	5	2026-02-06 16:30:00	2026-02-06 16:45:00	faltou	Transplante Capilar		f	\N	\N	2026-02-06 11:42:00.273149	\N	\N
236	204	5	2026-02-09 14:30:00	2026-02-09 14:45:00	agendado	Transplante Capilar		t	2026-02-09 17:23:21.282588	\N	2026-02-09 17:23:12.030463	\N	\N
248	216	5	2026-02-11 10:00:00	2026-02-11 10:15:00	atendido	UNIMED		f	2026-02-11 13:10:36.916536	\N	2026-02-11 12:08:32.162699	\N	\N
261	229	5	2026-02-12 10:00:00	2026-02-12 10:15:00	faltou	UNIMED		f	\N	\N	2026-02-11 20:35:31.418398	\N	\N
267	234	5	2026-02-12 15:30:00	2026-02-12 15:45:00	faltou	Particular		f	\N	\N	2026-02-11 20:39:13.188306	\N	\N
434	375	5	2026-03-06 09:00:00	2026-03-06 09:15:00	faltou	UNIMED		f	\N	\N	2026-03-06 11:51:25.752729	\N	\N
278	49	5	2026-02-13 14:30:00	2026-02-13 14:45:00	atendido	Retorno Botox		f	2026-02-13 16:32:01.75932	\N	2026-02-13 11:45:36.015449	\N	\N
400	345	5	2026-03-04 15:30:00	2026-03-04 15:45:00	atendido	Transplante Capilar		f	2026-03-04 18:36:47.901457	\N	2026-03-04 12:11:57.336006	\N	\N
285	248	5	2026-02-19 11:00:00	2026-02-19 11:15:00	atendido	Botox		f	2026-02-19 14:14:50.234483	\N	2026-02-13 18:15:51.579476	\N	\N
291	105	5	2026-02-20 09:30:00	2026-02-20 09:45:00	faltou	Retorno Botox		f	\N	\N	2026-02-13 18:18:29.518989	\N	\N
359	315	5	2026-03-02 14:30:00	2026-03-02 14:45:00	atendido	Retorno Botox		f	2026-03-02 17:45:53.649193	\N	2026-03-02 11:21:37.164148	\N	2026-01-28 17:30:00
294	256	5	2026-02-20 11:00:00	2026-02-20 11:15:00	atendido	Particular		f	2026-02-20 13:54:55.848504	\N	2026-02-13 18:19:35.915574	\N	\N
435	376	5	2026-03-06 09:15:00	2026-03-06 09:30:00	faltou	UNIMED		f	\N	\N	2026-03-06 12:11:11.927829	\N	\N
360	316	5	2026-03-02 14:45:00	2026-03-02 15:00:00	atendido	Retorno Botox		f	2026-03-02 17:46:09.845026	\N	2026-03-02 11:22:50.622087	\N	2026-01-26 17:45:00
308	268	5	2026-02-25 10:15:00	2026-02-25 10:30:00	atendido	UNIMED		f	2026-02-25 13:40:26.53352	\N	2026-02-24 19:38:54.303189	\N	\N
310	270	5	2026-02-25 11:00:00	2026-02-25 11:15:00	atendido	UNIMED		f	2026-02-25 14:01:18.932914	\N	2026-02-24 19:40:10.303871	\N	\N
313	273	5	2026-02-25 14:30:00	2026-02-25 14:45:00	atendido	UNIMED		f	2026-02-25 17:44:42.874297	\N	2026-02-24 19:43:02.928795	\N	\N
401	346	5	2026-03-04 16:30:00	2026-03-04 16:45:00	atendido	Transplante Capilar		f	2026-03-04 19:38:28.540217	\N	2026-03-04 12:12:20.737921	\N	\N
316	275	5	2026-02-25 16:00:00	2026-02-25 16:15:00	faltou	Transplante Capilar		f	\N	\N	2026-02-24 19:44:39.169571	\N	\N
334	290	5	2026-02-26 17:00:00	2026-02-26 17:15:00	agendado	Transplante Capilar		f	\N	\N	2026-02-26 11:32:47.208045	\N	\N
376	329	5	2026-03-03 15:30:00	2026-03-03 15:45:00	faltou	Particular		f	\N	\N	2026-03-03 11:56:41.892481	\N	\N
336	292	5	2026-02-26 10:14:00	2026-02-26 10:29:00	atendido	Particular		f	2026-02-26 13:20:29.283369	\N	2026-02-26 13:15:01.115369	\N	\N
402	347	5	2026-03-04 17:00:00	2026-03-04 17:15:00	atendido	Particular		f	2026-03-04 18:40:06.18773	\N	2026-03-04 12:12:39.660278	\N	\N
340	296	5	2026-02-27 10:30:00	2026-02-27 10:45:00	atendido	Transplante Capilar		f	2026-02-27 14:00:33.659541	\N	2026-02-27 13:22:28.666406	\N	2023-05-03 16:30:00
350	306	5	2026-02-27 17:15:00	2026-02-27 17:30:00	atendido	Retorno Botox		f	2026-02-27 19:57:05.696721	\N	2026-02-27 17:18:10.844168	\N	\N
392	229	5	2026-03-04 09:30:00	2026-03-04 09:45:00	atendido	Particular		f	2026-03-04 12:30:17.176402	\N	2026-03-04 12:06:22.794053	\N	\N
391	337	5	2026-03-04 09:00:00	2026-03-04 09:15:00	atendido	Particular		f	2026-03-04 12:06:02.2902	\N	2026-03-04 12:05:55.388055	\N	\N
409	354	7	2026-03-04 14:00:00	2026-03-04 14:15:00	agendado	Retorno		t	2026-03-04 17:04:34.188081	\N	2026-03-04 17:04:27.71551	\N	\N
403	348	7	2026-03-04 14:00:00	2026-03-04 14:15:00	faltou	Retorno		f	\N	\N	2026-03-04 12:14:45.373309	\N	\N
436	377	5	2026-03-06 09:30:00	2026-03-06 09:45:00	atendido	Transplante Capilar		f	2026-03-06 12:38:31.061951	\N	2026-03-06 12:11:32.937908	\N	\N
397	342	5	2026-03-04 14:30:00	2026-03-04 14:45:00	atendido	Botox		f	2026-03-04 17:33:54.633096	\N	2026-03-04 12:10:25.107727	\N	\N
398	343	5	2026-03-04 14:45:00	2026-03-04 15:00:00	atendido	Retorno 1 semana TX		f	2026-03-04 17:32:10.850362	\N	2026-03-04 12:11:15.188442	\N	\N
416	175	5	2026-03-05 10:00:00	2026-03-05 10:15:00	faltou	Retorno Botox		f	\N	\N	2026-03-05 12:00:08.249871	\N	\N
399	344	5	2026-03-04 15:00:00	2026-03-04 15:15:00	faltou	Particular		f	\N	\N	2026-03-04 12:11:35.817369	\N	\N
437	93	5	2026-03-06 10:00:00	2026-03-06 10:15:00	faltou	Particular		f	\N	\N	2026-03-06 12:11:55.693387	\N	\N
420	363	5	2026-03-05 14:30:00	2026-03-05 14:45:00	faltou	Particular		f	\N	\N	2026-03-05 12:05:07.469432	\N	\N
421	364	5	2026-03-05 14:45:00	2026-03-05 15:00:00	faltou	Particular		f	\N	\N	2026-03-05 12:05:51.698178	\N	\N
426	368	5	2026-03-05 16:45:00	2026-03-05 17:00:00	atendido	Retorno 1 semana TX		f	2026-03-05 18:33:54.399796	\N	2026-03-05 12:13:30.836571	\N	\N
425	182	5	2026-03-05 16:30:00	2026-03-05 16:45:00	faltou	Retorno Botox		f	\N	\N	2026-03-05 12:13:09.031397	\N	\N
438	332	5	2026-03-06 10:30:00	2026-03-06 10:45:00	faltou	Transplante Capilar		f	\N	\N	2026-03-06 12:12:28.227465	\N	\N
439	378	5	2026-03-06 11:00:00	2026-03-06 11:15:00	atendido	Particular		f	2026-03-06 13:45:13.658606	\N	2026-03-06 12:13:02.333105	\N	\N
444	381	5	2026-03-09 10:30:00	2026-03-09 10:45:00	atendido	Transplante Capilar		f	2026-03-09 13:19:07.931364	\N	2026-03-09 11:40:15.304223	\N	2025-02-17 13:30:00
440	379	5	2026-03-09 09:00:00	2026-03-09 09:15:00	atendido	Transplante Capilar		f	2026-03-09 12:21:34.38746	\N	2026-03-09 11:35:58.733063	\N	2025-02-18 12:00:00
441	259	5	2026-03-09 08:30:00	2026-03-09 12:30:00	atendido	Preenchimento		f	2026-03-09 11:36:40.604049	\N	2026-03-09 11:36:36.543285	\N	\N
445	105	5	2026-03-09 11:00:00	2026-03-09 11:15:00	atendido	Retorno Botox		f	2026-03-09 13:47:17.337826	\N	2026-03-09 11:40:38.685289	205	\N
442	380	5	2026-03-09 09:30:00	2026-03-09 09:45:00	atendido	Particular		f	2026-03-09 12:44:46.536853	\N	2026-03-09 11:37:07.11576	\N	\N
443	238	5	2026-03-09 10:00:00	2026-03-09 10:15:00	atendido	UNIMED		f	2026-03-09 12:52:17.289251	\N	2026-03-09 11:39:52.025939	\N	\N
449	385	5	2026-03-09 16:15:00	2026-03-09 16:30:00	atendido	Retorno 1 semana TX		f	2026-03-09 18:51:02.683599	\N	2026-03-09 11:43:53.596587	\N	\N
451	387	5	2026-03-09 17:00:00	2026-03-09 17:15:00	atendido	UNIMED		f	2026-03-09 20:05:23.212753	\N	2026-03-09 11:44:42.455206	\N	\N
447	383	5	2026-03-09 15:30:00	2026-03-09 15:45:00	atendido	Transplante Capilar		f	2026-03-09 18:35:22.035151	\N	2026-03-09 11:42:13.435505	\N	\N
448	384	5	2026-03-09 16:00:00	2026-03-09 16:15:00	faltou	Retorno Botox		f	\N	\N	2026-03-09 11:42:35.562857	\N	\N
450	386	5	2026-03-09 16:30:00	2026-03-09 16:45:00	faltou	Transplante Capilar		f	\N	\N	2026-03-09 11:44:28.03368	\N	\N
452	388	5	2026-03-10 09:00:00	2026-03-10 09:15:00	faltou	Particular		f	\N	\N	2026-03-10 11:16:49.590034	\N	\N
455	390	5	2026-03-10 10:00:00	2026-03-10 10:15:00	atendido	Botox		f	2026-03-10 12:31:49.53805	\N	2026-03-10 11:18:11.536802	\N	\N
156	130	5	2026-01-26 17:00:00	2026-01-26 17:15:00	atendido	Botox		f	2026-01-26 19:47:09.200279	\N	2026-01-26 17:47:23.127611	\N	\N
159	132	5	2026-01-27 10:00:00	2026-01-27 10:15:00	atendido	UNIMED		f	2026-01-27 14:29:26.211119	\N	2026-01-26 18:15:57.831235	\N	\N
201	172	5	2026-02-04 09:30:00	2026-02-04 09:45:00	agendado	Transplante Capilar		t	2026-02-04 12:31:13.019221	\N	2026-02-04 11:54:24.194315	\N	\N
161	134	5	2026-01-27 10:30:00	2026-01-27 10:45:00	atendido	UNIMED		f	2026-01-27 14:29:55.141887	\N	2026-01-26 18:26:45.183133	\N	\N
162	135	5	2026-01-27 10:45:00	2026-01-27 11:00:00	atendido	UNIMED		f	2026-01-27 14:29:58.810229	\N	2026-01-26 18:27:22.96937	\N	\N
167	140	5	2026-01-27 15:00:00	2026-01-27 15:15:00	agendado	Botox		t	2026-01-27 17:53:17.920766	\N	2026-01-26 18:29:41.338124	\N	\N
168	141	5	2026-01-27 15:15:00	2026-01-27 15:30:00	atendido	Transplante Capilar		f	2026-01-27 19:10:30.735436	\N	2026-01-26 18:30:56.25052	\N	\N
203	174	5	2026-02-04 10:30:00	2026-02-04 10:45:00	agendado	Transplante Capilar		t	2026-02-04 13:45:11.009557	\N	2026-02-04 11:55:06.750729	\N	\N
292	254	5	2026-02-20 10:00:00	2026-02-20 10:15:00	atendido	Retorno Botox		f	2026-02-20 13:55:01.65184	\N	2026-02-13 18:18:53.991752	\N	\N
302	103	5	2026-02-20 15:15:00	2026-02-20 15:30:00	atendido	Preenchimento		f	2026-02-20 18:07:07.51889	\N	2026-02-20 18:06:50.745188	\N	\N
255	223	5	2026-02-11 16:30:00	2026-02-11 16:45:00	atendido	Particular		f	2026-02-11 20:14:34.030165	\N	2026-02-11 12:11:17.808169	\N	\N
217	188	5	2026-02-05 16:45:00	2026-02-05 17:00:00	atendido	Particular		f	2026-02-05 19:10:47.954079	\N	2026-02-05 12:22:44.209805	\N	\N
216	187	5	2026-02-05 16:30:00	2026-02-05 16:45:00	atendido	Transplante Capilar		f	2026-02-05 20:50:46.484616	\N	2026-02-05 12:22:22.56548	\N	\N
227	195	5	2026-02-06 15:00:00	2026-02-06 15:15:00	faltou	Botox		f	\N	\N	2026-02-06 11:38:27.884976	\N	\N
237	205	5	2026-02-09 16:00:00	2026-02-09 16:15:00	agendado	Transplante Capilar		t	2026-02-09 19:08:27.026723	\N	2026-02-09 19:08:13.32246	\N	\N
257	225	5	2026-02-11 10:15:00	2026-02-11 10:30:00	atendido	UNIMED		f	2026-02-11 12:59:31.18491	\N	2026-02-11 12:57:04.61506	\N	\N
259	227	5	2026-02-12 09:00:00	2026-02-12 09:15:00	atendido	UNIMED		f	2026-02-12 12:14:13.292695	\N	2026-02-11 20:34:37.583004	\N	\N
262	230	5	2026-02-12 10:30:00	2026-02-12 10:45:00	faltou	Transplante Capilar		f	\N	\N	2026-02-11 20:36:11.076414	\N	\N
299	261	5	2026-02-20 16:30:00	2026-02-20 16:45:00	atendido	Botox		f	2026-02-20 19:28:15.619456	\N	2026-02-13 18:21:54.115044	\N	\N
265	232	5	2026-02-12 14:45:00	2026-02-12 15:00:00	atendido	Retorno Botox		f	2026-02-12 17:29:35.474357	\N	2026-02-11 20:37:43.390996	\N	\N
263	99	5	2026-02-12 11:00:00	2026-02-12 11:15:00	atendido	Retorno Botox		f	2026-02-12 13:54:14.364319	\N	2026-02-11 20:36:37.721553	\N	\N
269	236	5	2026-02-12 17:00:00	2026-02-12 17:15:00	agendado	Particular		t	2026-02-12 20:00:13.264574	\N	2026-02-11 20:40:20.935097	\N	\N
303	239	5	2026-02-23 08:30:00	2026-02-23 08:45:00	agendado	Preenchimento		t	2026-02-23 12:12:55.607246	\N	2026-02-23 12:11:07.491598	\N	\N
272	239	5	2026-02-13 09:30:00	2026-02-13 09:45:00	atendido	Botox		f	2026-02-13 12:34:06.474716	\N	2026-02-13 11:42:46.046229	\N	\N
273	240	5	2026-02-13 10:00:00	2026-02-13 10:15:00	atendido	Transplante Capilar		f	2026-02-13 12:34:10.922439	\N	2026-02-13 11:43:06.043427	\N	\N
277	47	5	2026-02-13 14:15:00	2026-02-13 14:30:00	atendido	Retorno Botox		f	2026-02-13 16:31:55.345584	\N	2026-02-13 11:45:21.771848	\N	\N
271	238	5	2026-02-13 09:51:00	2026-02-13 10:06:00	atendido	Particular		f	2026-02-13 12:49:06.230899	\N	2026-02-13 11:42:06.77699	\N	\N
281	245	5	2026-02-19 09:00:00	2026-02-19 09:15:00	faltou	UNIMED		f	\N	\N	2026-02-13 18:09:20.968612	\N	\N
305	265	5	2026-02-25 09:00:00	2026-02-25 09:15:00	atendido	Particular		f	2026-02-25 12:29:00.142559	\N	2026-02-24 19:36:52.517071	\N	\N
287	250	5	2026-02-19 15:30:00	2026-02-19 15:45:00	faltou	Transplante Capilar		f	\N	\N	2026-02-13 18:16:33.338291	\N	\N
327	284	5	2026-02-26 14:30:00	2026-02-26 14:45:00	agendado	Botox		f	\N	\N	2026-02-26 11:29:09.917019	\N	\N
286	249	5	2026-02-19 15:00:00	2026-02-19 15:15:00	atendido	Transplante Capilar		f	2026-02-19 19:45:01.837802	\N	2026-02-13 18:16:13.326332	\N	\N
301	263	5	2026-02-19 10:45:00	2026-02-19 11:00:00	atendido	Transplante Capilar		f	2026-02-19 13:34:53.535637	\N	2026-02-19 13:34:43.75316	\N	\N
309	269	5	2026-02-25 10:30:00	2026-02-25 10:45:00	faltou	Botox		f	\N	\N	2026-02-24 19:39:43.811215	\N	\N
290	253	5	2026-02-20 09:00:00	2026-02-20 09:15:00	faltou	Particular		f	\N	\N	2026-02-13 18:18:11.260395	\N	\N
326	283	5	2026-02-13 17:00:00	2026-02-13 21:00:00	atendido	Pequena Cirurgia		f	2026-02-26 13:47:20.578669	\N	2026-02-26 11:28:38.422282	\N	2026-02-26 20:00:00
314	274	5	2026-02-25 15:00:00	2026-02-25 15:15:00	atendido	UNIMED		f	2026-02-25 17:58:45.504126	\N	2026-02-24 19:43:37.208437	\N	\N
317	276	5	2026-02-25 16:30:00	2026-02-25 16:45:00	faltou	Transplante Capilar		f	\N	\N	2026-02-24 19:45:30.313734	\N	\N
318	277	5	2026-02-25 17:00:00	2026-02-25 17:15:00	faltou	Botox		f	\N	\N	2026-02-25 17:44:15.107111	\N	\N
333	289	5	2026-02-26 16:30:00	2026-02-26 16:45:00	agendado	Transplante Capilar		f	\N	\N	2026-02-26 11:31:52.299656	\N	\N
337	293	5	2026-02-27 09:00:00	2026-02-27 09:15:00	faltou	UNIMED		f	\N	\N	2026-02-27 13:20:48.849969	\N	\N
324	281	5	2026-02-26 10:00:00	2026-02-26 10:15:00	atendido	Particular		f	2026-02-26 12:49:04.231219	\N	2026-02-26 11:27:49.97299	\N	\N
321	62	5	2026-02-26 09:00:00	2026-02-26 09:15:00	agendado	Botox		f	2026-02-26 12:01:55.006558	\N	2026-02-26 11:23:50.174983	\N	\N
362	317	5	2026-03-02 16:00:00	2026-03-02 16:15:00	atendido	Retorno Botox		f	2026-03-02 18:58:16.480408	\N	2026-03-02 11:34:32.383995	\N	2026-02-02 19:00:00
352	308	5	2026-03-02 09:00:00	2026-03-02 09:15:00	atendido	Particular		f	2026-03-02 12:31:08.863872	\N	2026-03-02 11:07:10.163063	\N	\N
343	299	5	2026-02-27 14:45:00	2026-02-27 15:00:00	atendido	Retorno Botox		f	2026-02-27 18:23:00.796546	\N	2026-02-27 17:09:38.474065	\N	\N
367	321	5	2026-03-03 09:00:00	2026-03-03 09:15:00	atendido	UNIMED		f	2026-03-03 11:56:46.446188	\N	2026-03-03 11:10:30.887586	\N	\N
380	333	5	2026-03-03 17:00:00	2026-03-03 17:15:00	atendido	Particular		f	2026-03-03 20:08:14.024515	\N	2026-03-03 12:57:51.272482	\N	\N
355	311	5	2026-03-02 10:00:00	2026-03-02 10:15:00	atendido	UNIMED		f	2026-03-02 12:55:56.096725	\N	2026-03-02 11:19:14.813009	\N	\N
357	313	5	2026-03-02 10:30:00	2026-03-02 10:45:00	atendido	Particular		f	2026-03-02 13:14:09.866809	\N	2026-03-02 11:19:42.79421	\N	\N
358	314	5	2026-03-02 11:00:00	2026-03-02 11:15:00	atendido	Botox		f	2026-03-02 13:17:27.779399	\N	2026-03-02 11:20:19.317393	\N	2026-01-21 14:00:00
363	318	5	2026-03-02 16:15:00	2026-03-02 16:30:00	atendido	Transplante Capilar		f	2026-03-02 19:50:30.347863	\N	2026-03-02 11:35:05.298833	\N	\N
364	319	5	2026-03-02 16:30:00	2026-03-02 16:45:00	atendido	Botox		f	2026-03-02 19:50:35.532318	\N	2026-03-02 11:35:39.978773	\N	\N
365	180	5	2026-03-02 17:00:00	2026-03-02 17:15:00	atendido	Retorno Botox		f	2026-03-02 19:50:38.814543	\N	2026-03-02 11:36:15.576462	51	\N
369	323	5	2026-03-03 09:30:00	2026-03-03 09:45:00	atendido	Particular		f	2026-03-03 12:17:58.852771	\N	2026-03-03 11:11:24.453063	\N	\N
372	326	5	2026-03-03 10:15:00	2026-03-03 10:30:00	atendido	Particular		f	2026-03-03 12:53:15.702249	\N	2026-03-03 11:12:49.758097	\N	\N
377	330	5	2026-03-03 15:45:00	2026-03-03 16:00:00	atendido	Particular		f	2026-03-03 18:29:25.105732	\N	2026-03-03 11:58:28.892774	\N	\N
383	336	7	2026-03-04 07:00:00	2026-03-04 07:15:00	faltou	Particular		f	\N	\N	2026-03-04 11:31:55.482693	\N	\N
393	338	5	2026-03-04 10:00:00	2026-03-04 10:15:00	atendido	Particular		f	2026-03-04 13:07:50.068361	\N	2026-03-04 12:06:46.229258	\N	\N
395	340	5	2026-03-04 11:00:00	2026-03-04 11:15:00	atendido	Botox		f	2026-03-04 14:04:10.514097	\N	2026-03-04 12:07:59.404993	\N	\N
396	341	5	2026-03-04 11:15:00	2026-03-04 11:30:00	atendido	Botox		f	2026-03-04 13:58:12.196548	\N	2026-03-04 12:08:23.050097	\N	\N
410	355	7	2026-03-04 14:45:00	2026-03-04 15:00:00	agendado	Retorno		t	2026-03-04 17:05:35.412651	\N	2026-03-04 17:05:27.709399	\N	\N
406	351	7	2026-03-04 14:45:00	2026-03-04 15:00:00	agendado	Particular		t	2026-03-04 17:20:43.625157	\N	2026-03-04 12:24:01.700128	\N	\N
407	352	7	2026-03-04 15:00:00	2026-03-04 15:15:00	faltou	Particular		f	\N	\N	2026-03-04 12:24:23.10678	\N	\N
413	357	5	2026-03-05 09:00:00	2026-03-05 09:15:00	faltou	Particular		f	\N	\N	2026-03-05 11:30:38.390779	\N	\N
417	360	5	2026-03-05 10:30:00	2026-03-05 10:45:00	atendido	Transplante Capilar		f	2026-03-05 13:22:37.01524	\N	2026-03-05 12:00:44.936148	\N	\N
424	367	5	2026-03-05 16:00:00	2026-03-05 16:15:00	atendido	Particular		f	2026-03-05 19:03:57.181783	\N	2026-03-05 12:12:40.614687	\N	\N
432	373	5	2026-03-05 14:45:00	2026-03-05 15:00:00	faltou	Particular		f	\N	\N	2026-03-05 14:37:31.318918	\N	\N
422	365	5	2026-03-05 15:00:00	2026-03-05 15:15:00	atendido	UNIMED		f	2026-03-05 18:21:07.2715	\N	2026-03-05 12:06:15.180205	\N	\N
152	126	5	2026-01-26 15:00:00	2026-01-26 15:15:00	atendido	Transplante Capilar		f	2026-01-26 18:19:12.823294	\N	2026-01-26 17:40:22.644006	\N	\N
200	171	5	2026-02-04 09:00:00	2026-02-04 09:15:00	atendido	Transplante Capilar		f	2026-02-04 12:01:03.110955	\N	2026-02-04 11:54:02.700223	\N	\N
164	137	5	2026-01-27 11:15:00	2026-01-27 11:30:00	atendido	Retorno Botox		f	2026-01-27 13:29:05.709208	\N	2026-01-26 18:28:18.117515	\N	\N
165	138	5	2026-01-27 11:30:00	2026-01-27 11:45:00	atendido	Pequena Cirurgia		f	2026-01-27 13:30:08.80635	\N	2026-01-26 18:28:54.146209	\N	\N
172	145	5	2026-01-27 17:00:00	2026-01-27 17:15:00	agendado	Particular		t	2026-01-27 19:58:51.145528	\N	2026-01-26 18:36:13.374156	\N	\N
171	144	5	2026-01-27 16:30:00	2026-01-27 16:45:00	atendido	Transplante Capilar		f	2026-01-27 19:29:17.152703	\N	2026-01-26 18:35:46.322132	\N	\N
206	177	5	2026-02-05 09:00:00	2026-02-05 09:15:00	atendido	UNIMED		f	2026-02-05 12:14:55.067836	\N	2026-02-05 12:14:48.633742	\N	\N
304	264	5	2026-02-23 11:15:00	2026-02-23 11:30:00	agendado	Pequena Cirurgia		t	2026-02-23 14:22:18.029753	\N	2026-02-23 14:22:12.706487	\N	\N
211	182	5	2026-02-05 14:45:00	2026-02-05 15:00:00	atendido	UNIMED		f	2026-02-05 17:08:25.709073	\N	2026-02-05 12:19:12.903999	\N	\N
212	183	5	2026-02-05 15:15:00	2026-02-05 15:30:00	faltou	Transplante Capilar		f	\N	\N	2026-02-05 12:19:30.631584	\N	\N
258	226	5	2026-02-11 10:45:00	2026-02-11 11:00:00	atendido	Particular		f	2026-02-11 14:34:08.765409	\N	2026-02-11 13:58:40.246987	\N	\N
250	218	5	2026-02-11 11:00:00	2026-02-11 11:15:00	atendido	Laser		f	2026-02-11 13:57:31.304926	\N	2026-02-11 12:09:20.143869	\N	\N
214	185	5	2026-02-05 16:00:00	2026-02-05 16:15:00	faltou	UNIMED		f	\N	\N	2026-02-05 12:21:41.422565	\N	\N
247	215	5	2026-02-11 09:45:00	2026-02-11 10:00:00	atendido	Transplante Capilar		f	2026-02-11 13:10:38.883473	\N	2026-02-11 12:08:08.210143	102	\N
218	189	5	2026-02-06 09:00:00	2026-02-06 09:15:00	atendido	UNIMED		f	2026-02-06 12:02:28.081898	\N	2026-02-06 11:24:08.159978	\N	\N
221	192	5	2026-02-06 10:00:00	2026-02-06 10:15:00	atendido	Transplante Capilar		f	2026-02-06 13:02:45.531541	\N	2026-02-06 11:35:39.603304	\N	\N
225	95	5	2026-02-06 14:30:00	2026-02-06 14:45:00	agendado	Botox		t	2026-02-06 17:45:30.101225	\N	2026-02-06 11:37:40.611536	\N	\N
226	194	5	2026-02-06 14:45:00	2026-02-06 15:00:00	agendado	Transplante Capilar		t	2026-02-06 17:45:32.665099	\N	2026-02-06 11:38:04.277278	\N	\N
229	197	5	2026-02-06 16:00:00	2026-02-06 16:15:00	agendado	Particular		t	2026-02-06 18:59:42.192346	\N	2026-02-06 11:41:26.373434	\N	\N
251	219	5	2026-02-11 14:30:00	2026-02-11 14:45:00	atendido	Botox		f	2026-02-11 18:11:35.159098	\N	2026-02-11 12:09:42.390723	\N	\N
232	200	5	2026-02-09 10:00:00	2026-02-09 10:15:00	agendado	Transplante Capilar		t	2026-02-09 12:49:20.809924	\N	2026-02-09 12:49:17.997905	\N	\N
231	199	5	2026-02-09 09:00:00	2026-02-09 09:15:00	agendado	Transplante Capilar		t	2026-02-09 12:33:57.796433	\N	2026-02-09 12:33:54.55049	\N	\N
254	222	5	2026-02-11 16:00:00	2026-02-11 16:15:00	atendido	Laser		f	2026-02-11 19:18:48.436775	\N	2026-02-11 12:10:47.730693	\N	\N
233	201	5	2026-02-09 10:30:00	2026-02-09 10:45:00	faltou	Transplante Capilar		t	2026-02-09 14:13:02.846564	\N	2026-02-09 14:11:07.092975	\N	\N
234	202	5	2026-02-09 10:30:00	2026-02-09 10:45:00	faltou	Transplante Capilar		t	2026-02-09 14:13:04.47919	\N	2026-02-09 14:11:07.761175	\N	\N
238	206	5	2026-02-09 15:30:00	2026-02-09 15:45:00	faltou	Transplante Capilar		t	2026-02-09 19:09:09.424487	\N	2026-02-09 19:08:59.714538	\N	\N
239	207	5	2026-02-10 10:00:00	2026-02-10 10:15:00	faltou	Transplante Capilar		f	\N	\N	2026-02-10 12:17:44.005474	\N	\N
264	231	5	2026-02-12 14:30:00	2026-02-12 14:45:00	faltou	Particular		f	\N	\N	2026-02-11 20:37:10.331811	\N	\N
243	211	5	2026-02-10 15:00:00	2026-02-10 15:15:00	atendido	Transplante Capilar		f	2026-02-10 18:07:58.776129	\N	2026-02-10 12:22:39.044852	\N	\N
245	213	5	2026-02-11 09:00:00	2026-02-11 09:15:00	faltou	UNIMED		f	\N	\N	2026-02-11 12:06:13.941548	\N	\N
306	266	5	2026-02-25 09:30:00	2026-02-25 09:45:00	atendido	UNIMED		f	2026-02-25 12:29:03.822731	\N	2026-02-24 19:37:53.906037	\N	\N
270	237	5	2026-02-12 11:30:00	2026-02-12 11:45:00	agendado	Transplante Capilar		t	2026-02-12 19:01:50.721254	\N	2026-02-12 19:01:43.681891	\N	\N
311	271	5	2026-02-25 11:15:00	2026-02-25 11:30:00	atendido	Infiltração Capilar		f	2026-02-25 14:16:37.099041	\N	2026-02-24 19:40:38.690661	\N	\N
274	241	5	2026-02-13 10:30:00	2026-02-13 10:45:00	faltou	UNIMED		f	\N	\N	2026-02-13 11:43:28.759633	\N	\N
276	46	5	2026-02-13 14:00:00	2026-02-13 14:15:00	atendido	Retorno Botox		f	2026-02-13 16:31:52.656371	\N	2026-02-13 11:45:08.545645	\N	\N
315	127	5	2026-02-25 15:30:00	2026-02-25 15:45:00	faltou	Botox		f	\N	\N	2026-02-24 19:43:54.046285	\N	\N
300	262	5	2026-02-13 15:30:00	2026-02-13 15:45:00	atendido	Botox		f	2026-02-13 18:23:19.897436	\N	2026-02-13 18:23:15.824013	\N	\N
282	246	5	2026-02-19 09:30:00	2026-02-19 09:45:00	atendido	Transplante Capilar		f	2026-02-19 12:28:05.173026	\N	2026-02-13 18:09:44.752042	\N	\N
338	294	5	2026-02-27 09:30:00	2026-02-27 09:45:00	faltou	Particular		f	\N	\N	2026-02-27 13:21:10.270382	\N	\N
319	278	5	2026-02-25 12:30:00	2026-02-25 12:45:00	atendido	Transplante Capilar		f	2026-02-25 19:07:30.049857	\N	2026-02-25 19:07:08.153123	\N	\N
320	279	5	2026-02-25 17:15:00	2026-02-25 17:30:00	atendido	Retorno		f	2026-02-25 20:05:42.852448	\N	2026-02-25 20:01:12.129965	\N	\N
293	255	5	2026-02-20 10:30:00	2026-02-20 10:45:00	atendido	Transplante Capilar		f	2026-02-20 14:01:44.816925	\N	2026-02-13 18:19:20.156055	\N	\N
295	257	5	2026-02-20 14:30:00	2026-02-20 14:45:00	atendido	Retorno Botox		f	2026-02-20 18:07:09.322928	\N	2026-02-13 18:20:19.042801	\N	\N
298	260	5	2026-02-20 16:00:00	2026-02-20 16:15:00	atendido	Transplante Capilar		f	2026-02-20 19:18:24.673178	\N	2026-02-13 18:21:37.048184	\N	\N
323	280	5	2026-02-26 09:30:00	2026-02-26 09:45:00	faltou	Transplante Capilar		f	\N	\N	2026-02-26 11:27:30.423164	\N	\N
325	282	5	2026-02-26 10:30:00	2026-02-26 10:45:00	atendido	UNIMED		f	2026-02-26 13:20:22.659477	\N	2026-02-26 11:28:13.168975	\N	\N
331	288	5	2026-02-26 16:00:00	2026-02-26 16:15:00	atendido	Botox		f	2026-02-27 13:21:00.790598	\N	2026-02-26 11:31:09.465649	\N	\N
342	298	5	2026-02-27 14:30:00	2026-02-27 14:45:00	faltou	Retorno Botox		f	\N	\N	2026-02-27 13:23:12.614169	\N	\N
353	309	5	2026-03-02 09:30:00	2026-03-02 09:45:00	atendido	Particular		f	2026-03-02 12:31:58.82339	\N	2026-03-02 11:18:20.36237	\N	2026-02-02 12:30:00
345	301	5	2026-02-27 15:45:00	2026-02-27 16:00:00	faltou	Retorno Botox		f	\N	\N	2026-02-27 17:11:47.38465	\N	\N
349	305	5	2026-02-27 17:00:00	2026-02-27 17:15:00	atendido	Botox		f	2026-02-27 18:57:18.08401	\N	2026-02-27 17:17:50.755179	\N	\N
329	286	5	2026-02-26 15:15:00	2026-02-26 15:30:00	atendido	Retorno 1 semana TX		f	2026-02-28 01:49:38.610634	\N	2026-02-26 11:30:24.520812	\N	\N
361	259	5	2026-03-02 15:00:00	2026-03-02 15:15:00	faltou	Preenchimento		f	\N	\N	2026-03-02 11:23:13.377801	\N	\N
370	324	5	2026-03-03 09:45:00	2026-03-03 10:00:00	atendido	Particular		f	2026-03-03 12:25:56.702528	\N	2026-03-03 11:11:40.235566	\N	\N
366	320	5	2026-03-02 15:15:00	2026-03-02 15:30:00	atendido	Retorno Botox		f	2026-03-02 18:07:18.801078	\N	2026-03-02 18:07:11.894028	\N	2026-02-02 18:15:00
378	331	5	2026-03-03 07:45:00	2026-03-03 08:00:00	faltou	Particular		f	\N	\N	2026-03-03 12:08:01.90111	\N	\N
375	328	5	2026-03-03 15:00:00	2026-03-03 15:15:00	atendido	Retirada de Ponto		f	2026-03-03 17:50:05.554426	\N	2026-03-03 11:54:58.581345	\N	2025-11-27 18:00:00
368	322	5	2026-03-03 09:15:00	2026-03-03 09:30:00	atendido	Particular		f	2026-03-03 12:08:19.730109	\N	2026-03-03 11:10:56.826526	\N	\N
371	325	5	2026-03-03 10:00:00	2026-03-03 10:15:00	atendido	Particular		f	2026-03-03 12:22:40.31658	\N	2026-03-03 11:12:11.419763	\N	\N
381	334	5	2026-03-03 14:45:00	2026-03-03 15:00:00	atendido	Transplante Capilar		f	2026-03-03 17:36:23.196068	\N	2026-03-03 17:35:54.611128	\N	\N
374	307	5	2026-03-03 10:45:00	2026-03-03 11:00:00	faltou	Retorno		f	\N	\N	2026-03-03 11:13:43.400972	\N	\N
394	339	5	2026-03-04 10:30:00	2026-03-04 10:45:00	faltou	Retorno Botox		f	\N	\N	2026-03-04 12:07:09.160382	\N	\N
405	350	7	2026-03-04 14:15:00	2026-03-04 14:30:00	faltou	Particular		f	\N	\N	2026-03-04 12:23:44.311613	\N	\N
411	356	5	2026-03-04 17:15:00	2026-03-04 17:30:00	atendido	Botox		f	2026-03-04 19:42:03.284468	\N	2026-03-04 19:41:54.858705	\N	\N
414	358	5	2026-03-05 09:00:00	2026-03-05 09:15:00	atendido	Retorno		f	2026-03-05 11:51:57.015834	\N	2026-03-05 11:51:12.191572	\N	\N
428	307	5	2026-03-05 11:15:00	2026-03-05 11:30:00	atendido	Retorno		f	\N	\N	2026-03-05 14:17:58.304374	\N	\N
429	324	5	2026-03-05 12:33:00	2026-03-05 12:48:00	faltou	Particular		f	\N	\N	2026-03-05 14:33:24.229662	\N	\N
423	366	5	2026-03-05 15:30:00	2026-03-05 15:45:00	atendido	Transplante Capilar		f	2026-03-05 18:19:57.071223	\N	2026-03-05 12:11:51.554862	\N	\N
427	369	5	2026-03-05 17:00:00	2026-03-05 17:15:00	atendido	Botox		f	2026-03-05 19:57:22.036906	\N	2026-03-05 12:13:50.606957	\N	\N
166	139	5	2026-01-27 14:30:00	2026-01-27 14:45:00	agendado	Transplante Capilar		f	\N	\N	2026-01-26 18:29:20.456058	\N	\N
191	106	5	2026-02-03 14:30:00	2026-02-03 14:45:00	atendido	Transplante Capilar		f	2026-02-03 17:24:47.672721	\N	2026-02-03 11:29:41.118169	\N	\N
177	150	5	2026-02-02 10:30:00	2026-02-02 10:45:00	agendado	Transplante Capilar		f	\N	\N	2026-02-02 13:39:37.431655	\N	\N
179	152	5	2026-02-02 14:30:00	2026-02-02 14:45:00	agendado	Retorno		f	\N	\N	2026-02-02 13:40:24.604704	\N	\N
182	155	5	2026-02-02 15:30:00	2026-02-02 15:45:00	agendado	UNIMED		f	\N	\N	2026-02-02 13:45:43.093907	\N	\N
205	176	5	2026-02-04 17:00:00	2026-02-04 17:15:00	agendado	Botox		t	2026-02-04 19:56:20.11208	\N	2026-02-04 19:56:06.761271	\N	\N
185	158	5	2026-02-02 17:00:00	2026-02-02 17:15:00	agendado	Botox		f	\N	\N	2026-02-02 13:48:23.002043	\N	\N
176	149	5	2026-02-02 10:00:00	2026-02-02 10:15:00	atendido	UNIMED		f	2026-02-02 14:14:07.796648	\N	2026-02-02 13:39:17.83615	\N	\N
174	147	5	2026-02-02 09:00:00	2026-02-02 09:15:00	atendido	Particular		f	2026-02-02 14:03:23.28667	\N	2026-02-02 13:37:07.463346	\N	\N
249	217	5	2026-02-11 10:30:00	2026-02-11 10:45:00	atendido	UNIMED		f	2026-02-11 13:57:26.837298	\N	2026-02-11 12:08:59.228841	\N	\N
175	148	5	2026-02-02 09:30:00	2026-02-02 09:45:00	faltou	Transplante Capilar		f	\N	\N	2026-02-02 13:37:55.254809	\N	\N
178	151	5	2026-02-02 11:00:00	2026-02-02 11:15:00	atendido	Particular		f	2026-02-02 14:02:58.468594	\N	2026-02-02 13:39:54.994168	\N	\N
186	159	5	2026-02-02 12:00:00	2026-02-02 12:15:00	atendido	Botox		f	2026-02-02 14:48:58.576241	\N	2026-02-02 14:48:50.358653	\N	\N
209	180	5	2026-02-05 10:30:00	2026-02-05 10:45:00	atendido	Botox		f	2026-02-05 14:02:12.198606	\N	2026-02-05 12:18:09.659402	\N	\N
288	251	5	2026-02-19 16:00:00	2026-02-19 16:15:00	faltou	UNIMED		f	\N	\N	2026-02-13 18:16:46.878061	\N	\N
180	153	5	2026-02-02 14:45:00	2026-02-02 15:00:00	atendido	Retorno 1 semana TX		f	2026-02-02 17:48:14.169239	\N	2026-02-02 13:41:03.24877	\N	\N
183	156	5	2026-02-02 16:00:00	2026-02-02 16:15:00	agendado	Particular		t	2026-02-02 19:20:18.486349	\N	2026-02-02 13:46:22.506231	\N	\N
184	157	5	2026-02-02 16:30:00	2026-02-02 16:45:00	agendado	Transplante Capilar		t	2026-02-02 19:52:37.794164	\N	2026-02-02 13:47:49.842206	\N	\N
187	160	5	2026-02-02 13:30:00	2026-02-02 13:45:00	agendado	Particular		t	2026-02-02 20:10:49.536046	\N	2026-02-02 20:06:27.95272	\N	\N
192	163	5	2026-02-03 15:00:00	2026-02-03 15:15:00	agendado	UNIMED		f	\N	\N	2026-02-03 11:30:14.791113	\N	\N
193	164	5	2026-02-03 15:30:00	2026-02-03 15:45:00	agendado	Transplante Capilar		f	\N	\N	2026-02-03 11:30:30.997441	\N	\N
194	165	5	2026-02-03 16:00:00	2026-02-03 16:15:00	agendado	Particular		f	\N	\N	2026-02-03 11:30:57.126263	\N	\N
195	166	5	2026-02-03 16:30:00	2026-02-03 16:45:00	agendado	Transplante Capilar		f	\N	\N	2026-02-03 11:31:19.454033	\N	\N
196	167	5	2026-02-03 17:00:00	2026-02-03 17:15:00	agendado	UNIMED		f	\N	\N	2026-02-03 11:31:48.723285	\N	\N
207	178	5	2026-02-05 09:30:00	2026-02-05 09:45:00	faltou	Transplante Capilar		f	\N	\N	2026-02-05 12:17:21.820023	\N	\N
213	184	5	2026-02-05 15:30:00	2026-02-05 15:45:00	atendido	Transplante Capilar		f	2026-02-05 18:52:40.834561	\N	2026-02-05 12:21:15.900581	\N	\N
188	118	5	2026-02-03 09:00:00	2026-02-03 09:15:00	atendido	Transplante Capilar		f	2026-02-03 12:36:23.46918	\N	2026-02-03 11:20:07.233609	\N	\N
189	161	5	2026-02-03 09:30:00	2026-02-03 09:45:00	atendido	UNIMED		t	2026-02-03 12:36:28.280944	\N	2026-02-03 11:20:38.067112	\N	\N
197	168	5	2026-02-03 10:00:00	2026-02-03 10:15:00	atendido	Botox		t	2026-02-03 12:53:44.360925	\N	2026-02-03 12:53:39.899514	\N	\N
252	220	5	2026-02-11 15:00:00	2026-02-11 15:15:00	atendido	Botox		f	2026-02-11 18:11:58.154183	\N	2026-02-11 12:10:07.308943	\N	\N
198	169	5	2026-02-03 11:00:00	2026-02-03 11:15:00	atendido	UNIMED		f	2026-02-03 14:04:35.536184	\N	2026-02-03 14:04:28.046779	\N	\N
190	162	5	2026-02-03 11:00:00	2026-02-03 11:15:00	atendido	Laser		f	2026-02-03 13:20:59.146235	\N	2026-02-03 11:29:05.819404	\N	\N
219	190	5	2026-02-06 09:15:00	2026-02-06 09:30:00	atendido	UNIMED		f	2026-02-06 12:08:31.079534	\N	2026-02-06 11:34:53.152851	\N	\N
220	191	5	2026-02-06 09:30:00	2026-02-06 09:45:00	faltou	UNIMED		f	\N	\N	2026-02-06 11:35:13.428422	\N	\N
228	196	5	2026-02-06 15:30:00	2026-02-06 15:45:00	agendado	Transplante Capilar		t	2026-02-06 17:45:35.677715	\N	2026-02-06 11:39:42.26455	\N	\N
235	203	5	2026-02-09 11:00:00	2026-02-09 11:15:00	agendado	Transplante Capilar		t	2026-02-09 14:13:05.766537	\N	2026-02-09 14:11:30.44507	\N	\N
266	233	5	2026-02-12 15:00:00	2026-02-12 15:15:00	atendido	Transplante Capilar		f	2026-02-12 17:22:57.907936	\N	2026-02-11 20:38:25.012407	\N	\N
240	208	5	2026-02-10 10:30:00	2026-02-10 10:45:00	faltou	Transplante Capilar		f	\N	\N	2026-02-10 12:18:12.628453	\N	\N
268	235	5	2026-02-12 16:00:00	2026-02-12 16:15:00	agendado	Transplante Capilar		t	2026-02-12 18:44:18.396619	\N	2026-02-11 20:39:57.814481	\N	\N
241	209	5	2026-02-10 11:00:00	2026-02-10 11:15:00	faltou	Retorno 1 semana TX		f	\N	\N	2026-02-10 12:21:29.931556	\N	\N
242	210	5	2026-02-10 14:30:00	2026-02-10 14:45:00	faltou	Transplante Capilar		f	\N	\N	2026-02-10 12:21:51.14883	\N	\N
244	212	5	2026-02-10 15:30:00	2026-02-10 15:45:00	agendado	Transplante Capilar		t	2026-02-10 18:08:01.571507	\N	2026-02-10 12:22:54.597577	\N	\N
246	214	5	2026-02-11 09:30:00	2026-02-11 09:45:00	faltou	Retirada de Ponto		f	\N	\N	2026-02-11 12:07:04.605701	\N	\N
289	252	5	2026-02-19 16:30:00	2026-02-19 16:45:00	atendido	Transplante Capilar		f	2026-02-19 19:44:56.05658	\N	2026-02-13 18:17:06.456928	\N	\N
296	258	5	2026-02-20 15:30:00	2026-02-20 15:45:00	faltou	Transplante Capilar		f	\N	\N	2026-02-13 18:20:37.931778	\N	\N
275	242	5	2026-02-13 11:00:00	2026-02-13 11:15:00	atendido	Retorno 1 semana TX		f	2026-02-13 17:38:35.808026	\N	2026-02-13 11:44:45.053487	\N	\N
379	332	5	2026-03-03 16:00:00	2026-03-03 16:15:00	faltou	Particular		f	\N	\N	2026-03-03 12:56:17.781194	\N	\N
279	243	5	2026-02-13 15:00:00	2026-02-13 15:15:00	atendido	Particular		f	2026-02-13 17:24:35.945127	\N	2026-02-13 11:45:55.669928	\N	\N
339	295	5	2026-02-27 10:00:00	2026-02-27 10:15:00	atendido	Particular		f	2026-02-27 13:21:47.629885	\N	2026-02-27 13:21:45.056888	\N	\N
280	244	5	2026-02-13 15:00:00	2026-02-13 15:15:00	atendido	Botox		f	\N	\N	2026-02-13 11:47:04.073308	\N	\N
373	327	5	2026-03-03 10:30:00	2026-03-03 10:45:00	faltou	Retorno		f	\N	\N	2026-03-03 11:13:24.434615	\N	\N
283	247	5	2026-02-19 10:00:00	2026-02-19 10:15:00	atendido	UNIMED		f	2026-02-19 13:19:08.111845	\N	2026-02-13 18:12:01.961239	\N	\N
341	297	5	2026-02-27 11:00:00	2026-02-27 11:15:00	atendido	Particular		f	2026-02-27 13:42:37.717076	\N	2026-02-27 13:22:51.34393	\N	2026-02-27 14:00:00
284	135	5	2026-02-19 10:30:00	2026-02-19 10:45:00	atendido	Retorno		f	2026-02-19 13:34:59.178665	\N	2026-02-13 18:12:40.595632	\N	\N
307	267	5	2026-02-25 10:00:00	2026-02-25 10:15:00	atendido	UNIMED		f	2026-02-25 13:40:28.44863	\N	2026-02-24 19:38:32.961544	\N	\N
328	285	5	2026-02-26 15:00:00	2026-02-26 15:15:00	agendado	Botox		f	\N	\N	2026-02-26 11:29:35.029984	\N	\N
330	287	5	2026-02-26 15:30:00	2026-02-26 15:45:00	agendado	Transplante Capilar		f	\N	\N	2026-02-26 11:30:48.902564	\N	\N
335	291	5	2026-02-26 11:15:00	2026-02-26 11:30:00	atendido	Botox		f	2026-02-26 13:47:24.628361	\N	2026-02-26 13:01:26.192648	\N	\N
351	307	5	2026-02-27 15:15:00	2026-02-27 15:30:00	atendido	Particular		f	2026-02-27 17:41:08.81745	\N	2026-02-27 17:41:02.687451	\N	2026-02-20 18:15:00
354	310	5	2026-03-02 09:45:00	2026-03-02 10:00:00	atendido	Transplante Capilar		f	2026-03-02 12:32:31.509208	\N	2026-03-02 11:18:47.309814	\N	\N
346	302	5	2026-02-27 16:00:00	2026-02-27 16:15:00	atendido	Retorno Botox		f	2026-02-27 18:57:49.878255	\N	2026-02-27 17:13:12.226695	\N	\N
348	304	5	2026-02-27 16:45:00	2026-02-27 17:00:00	faltou	Particular		f	\N	\N	2026-02-27 17:17:13.066445	\N	\N
382	335	5	2026-03-03 17:00:00	2026-03-03 17:15:00	atendido	Particular		f	2026-03-03 18:47:20.964945	\N	2026-03-03 18:46:35.784771	\N	\N
408	353	7	2026-03-04 15:30:00	2026-03-04 15:45:00	faltou	Particular		f	\N	\N	2026-03-04 12:24:46.822526	\N	\N
404	349	7	2026-03-04 15:00:00	2026-03-04 15:15:00	faltou	Retorno		f	\N	\N	2026-03-04 12:18:06.659797	\N	\N
412	160	5	2026-03-04 17:30:00	2026-03-04 17:45:00	atendido	Particular		f	2026-03-04 20:07:33.061976	\N	2026-03-04 20:07:26.539374	\N	\N
419	362	5	2026-03-05 11:00:00	2026-03-05 11:15:00	agendado	Pequena Cirurgia		t	2026-03-05 14:06:11.108834	\N	2026-03-05 12:01:52.947585	\N	\N
415	359	5	2026-03-05 09:30:00	2026-03-05 09:45:00	faltou	Transplante Capilar		f	\N	\N	2026-03-05 11:59:23.10353	\N	\N
418	324	5	2026-03-05 10:45:00	2026-03-05 11:00:00	agendado	Preenchimento		t	2026-03-05 14:06:13.862733	\N	2026-03-05 12:01:13.983772	\N	\N
431	372	5	2026-03-05 14:15:00	2026-03-05 14:30:00	faltou	Pequena Cirurgia		f	\N	\N	2026-03-05 14:36:31.183297	\N	\N
430	324	5	2026-03-05 19:34:00	2026-03-05 19:49:00	faltou	Particular		f	\N	\N	2026-03-05 14:34:31.384293	\N	\N
433	374	5	2026-03-05 14:45:00	2026-03-05 15:00:00	atendido	Retorno		f	2026-03-05 18:12:16.772243	\N	2026-03-05 17:27:04.533212	\N	\N
453	389	5	2026-03-10 09:30:00	2026-03-10 09:45:00	faltou	Transplante Capilar		f	\N	\N	2026-03-10 11:17:08.645326	\N	\N
456	391	5	2026-03-10 10:30:00	2026-03-10 10:45:00	faltou	UNIMED		f	\N	\N	2026-03-10 11:18:38.512183	\N	\N
461	396	5	2026-03-10 16:30:00	2026-03-10 16:45:00	atendido	Retorno 1 semana TX		f	2026-03-10 17:09:19.38169	\N	2026-03-10 11:21:03.434254	68	\N
460	395	5	2026-03-10 15:30:00	2026-03-10 15:45:00	atendido	Transplante Capilar		f	2026-03-10 18:25:34.862661	\N	2026-03-10 11:20:30.585767	\N	\N
446	382	5	2026-03-09 15:00:00	2026-03-09 15:15:00	atendido	Particular		f	2026-03-09 18:05:35.14543	\N	2026-03-09 11:41:58.132922	\N	\N
458	393	5	2026-03-10 15:00:00	2026-03-10 15:15:00	atendido	Botox		f	2026-03-10 18:19:50.340852	\N	2026-03-10 11:19:58.496319	\N	\N
459	394	5	2026-03-10 15:15:00	2026-03-10 15:30:00	atendido	Botox		f	2026-03-10 18:19:52.293776	\N	2026-03-10 11:20:14.237739	\N	\N
457	392	5	2026-03-10 14:30:00	2026-03-10 14:45:00	atendido	UNIMED		f	2026-03-10 18:11:59.979903	\N	2026-03-10 11:19:02.14331	\N	\N
462	397	5	2026-03-10 16:00:00	2026-03-10 16:15:00	faltou	Botox		f	\N	\N	2026-03-10 11:21:23.885264	\N	\N
454	175	5	2026-03-10 10:00:00	2026-03-10 10:15:00	atendido	Retorno Botox		f	2026-03-10 12:54:23.628956	\N	2026-03-10 11:17:29.488145	422	\N
476	61	5	2026-03-12 11:15:00	2026-03-12 11:30:00	atendido	Botox		f	2026-03-12 13:34:50.546889	\N	2026-03-11 11:49:55.550543	225	\N
463	219	5	2026-03-11 08:00:00	2026-03-11 08:15:00	atendido	Particular		f	2026-03-11 11:07:02.520133	\N	2026-03-11 11:06:36.257765	\N	\N
484	411	5	2026-03-11 09:30:00	2026-03-11 09:45:00	atendido	Transplante Capilar		f	2026-03-11 12:33:00.356698	\N	2026-03-11 12:32:53.186412	\N	\N
464	398	5	2026-03-11 09:00:00	2026-03-11 09:15:00	atendido	Particular		f	2026-03-11 13:00:59.724196	\N	2026-03-11 11:33:10.745982	\N	\N
467	225	5	2026-03-11 11:00:00	2026-03-11 11:15:00	faltou	Retorno Botox		f	\N	\N	2026-03-11 11:34:39.335916	\N	\N
485	412	5	2026-03-11 11:15:00	2026-03-11 11:30:00	atendido	Particular		f	2026-03-11 14:24:16.705811	\N	2026-03-11 14:24:05.754866	\N	\N
466	399	5	2026-03-11 10:30:00	2026-03-11 10:45:00	atendido	Transplante Capilar		f	2026-03-11 13:33:52.454297	\N	2026-03-11 11:34:01.004836	\N	\N
468	220	5	2026-03-11 14:30:00	2026-03-11 14:45:00	faltou	Retorno Botox		f	\N	\N	2026-03-11 11:34:54.605463	\N	\N
465	135	5	2026-03-11 10:00:00	2026-03-11 10:15:00	atendido	Retorno		f	2026-03-11 13:54:19.669062	\N	2026-03-11 11:33:33.752824	\N	\N
469	400	5	2026-03-11 15:30:00	2026-03-11 15:45:00	atendido	Transplante Capilar		f	2026-03-11 18:01:54.657032	\N	2026-03-11 11:35:25.094991	\N	\N
486	413	5	2026-03-12 18:00:00	2026-03-12 18:30:00	atendido	Transplante Capilar		f	2026-03-11 19:13:24.910785	\N	2026-03-11 19:08:58.760113	\N	\N
471	402	5	2026-03-11 16:30:00	2026-03-11 16:45:00	atendido	Transplante Capilar		f	2026-03-11 19:02:25.749246	\N	2026-03-11 11:36:18.920576	\N	\N
470	401	5	2026-03-11 16:00:00	2026-03-11 16:15:00	faltou	Particular		f	\N	\N	2026-03-11 11:35:47.790933	\N	\N
478	407	5	2026-03-12 14:30:00	2026-03-12 14:45:00	faltou	UNIMED		f	\N	\N	2026-03-11 11:51:45.300874	\N	\N
472	403	5	2026-03-12 09:00:00	2026-03-12 09:15:00	faltou	UNIMED		f	\N	\N	2026-03-11 11:37:49.595213	\N	\N
473	404	5	2026-03-12 09:30:00	2026-03-12 09:45:00	atendido	Particular		f	2026-03-12 11:51:18.618336	\N	2026-03-11 11:41:58.896494	\N	\N
492	420	5	2026-03-12 15:15:00	2026-03-12 15:30:00	atendido	Soroterapia		f	2026-03-12 18:06:30.674553	\N	2026-03-12 18:06:24.729319	\N	\N
474	405	5	2026-03-12 10:15:00	2026-03-12 10:30:00	atendido	Particular		f	2026-03-12 13:16:22.916272	\N	2026-03-11 11:49:19.934366	\N	\N
481	409	5	2026-03-12 15:45:00	2026-03-12 16:00:00	faltou	Botox		f	\N	\N	2026-03-11 11:57:07.175511	\N	\N
475	406	5	2026-03-12 10:30:00	2026-03-12 10:45:00	faltou	Transplante Capilar		f	\N	\N	2026-03-11 11:49:34.549897	\N	\N
477	363	5	2026-03-12 14:30:00	2026-03-12 14:45:00	atendido	Particular		f	2026-03-12 13:34:58.615481	\N	2026-03-11 11:50:48.551713	11	\N
479	408	5	2026-03-12 15:00:00	2026-03-12 15:15:00	atendido	Particular		f	2026-03-12 17:58:20.939295	\N	2026-03-11 11:52:06.798079	\N	\N
480	224	5	2026-03-12 15:30:00	2026-03-12 15:45:00	atendido	Particular		f	2026-03-12 18:28:34.46307	\N	2026-03-11 11:54:56.754272	\N	\N
482	307	5	2026-03-12 16:00:00	2026-03-12 16:15:00	faltou	Particular		f	\N	\N	2026-03-11 11:57:27.199159	\N	\N
491	419	5	2026-03-12 16:00:00	2026-03-12 16:15:00	atendido	Botox		f	2026-03-12 19:03:59.025614	\N	2026-03-12 17:53:18.229363	\N	\N
483	410	5	2026-03-12 16:30:00	2026-03-12 16:45:00	faltou	Transplante Capilar		f	\N	\N	2026-03-11 11:57:57.550273	\N	\N
\.


--
-- Data for Name: attachment; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.attachment (id, doctor_id, doctor_patient_id, owner_type, owner_id, file_path, label, created_at) FROM stdin;
\.


--
-- Data for Name: budget_cp; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.budget_cp (id, encounter_id, items, all_in_price, currency) FROM stdin;
1	1	{}	\N	BRL
2	2	{}	\N	BRL
\.


--
-- Data for Name: chat_message; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.chat_message (id, sender_id, recipient_id, message, created_at, read) FROM stdin;
1	5	4	TESTANDO	2025-12-05 17:47:35.889341	f
2	4	5	JA DEU CERTO VALDACIRA PAGOU 2000 REAIS DO RADIESSE ESTA AGUARDANDO	2025-12-09 19:18:14.484414	f
3	5	4	e o botox?	2025-12-09 19:28:03.160232	f
4	4	5	ELA DISSE QUE JA HAVIA FEITO	2025-12-09 20:29:06.120719	f
5	4	5	foi feito 3600 no debito	2025-12-09 20:55:10.144173	f
6	5	4	TEM ALGUIM CHECKOUT AI?	2025-12-11 15:23:59.724752	f
7	5	4	MINCHELE VC COLOCOU A FICHA DA FILHA DO MILTON?	2026-02-11 14:24:41.950382	f
8	5	4	testando	2026-02-27 17:46:28.818123	f
9	5	4	teste	2026-02-27 19:34:24.347152	f
10	5	4	teste	2026-02-27 20:01:53.330544	f
11	5	4	testando	2026-03-02 11:36:18.809074	f
12	5	4	apareceu /	2026-03-02 11:38:31.671947	f
13	5	4	ouviu?	2026-03-02 08:39:53.564542	f
14	5	4	ouviu??	2026-03-02 08:40:03.657069	f
15	4	5	O SOM ESTA LIGADO MAS NAO FEZ BARULHO	2026-03-02 11:40:16.666979	f
16	5	4	e agora	2026-03-02 08:52:26.255489	f
17	5	4	e agora	2026-03-02 08:59:43.069586	f
18	5	4	e agora	2026-03-02 09:14:45.732778	f
19	5	4	oi	2026-03-02 09:26:11.209754	f
20	5	4	teste	2026-03-02 09:27:26.377392	f
21	5	4	teste	2026-03-02 09:28:50.680581	f
22	5	4	teste	2026-03-02 09:38:09.603588	f
23	5	4	teste	2026-03-02 09:39:12.277573	f
24	5	4	teste	2026-03-02 10:18:29.168722	f
25	5	4	teste	2026-03-02 10:21:08.615039	f
26	5	4	teste	2026-03-02 10:24:04.552817	f
27	5	4	teste	2026-03-02 11:02:22.804785	f
28	5	4	chegou essa mensagem?	2026-03-02 16:38:29.27486	f
29	4	5	mensagem chegou sim, somente ainda nao faz barulho e nem sobe mensagem	2026-03-02 17:39:48.403706	f
30	5	4	Chegou	2026-03-10 23:02:55.865285	f
31	4	5	OI	2026-03-11 14:49:32.152758	f
32	5	4	testando	2026-03-11 14:50:18.698744	f
33	4	5	BOA TARDE	2026-03-11 14:54:12.401697	f
34	4	5	BOA TARDE	2026-03-11 14:54:40.214161	f
35	5	4	mensagem teste	2026-03-11 14:55:20.898499	f
36	12	11	oi	2026-03-11 15:06:03.666277	f
37	5	10	mensagem teste	2026-03-11 15:06:30.992261	f
38	5	12	mensagem teste	2026-03-11 15:06:34.995958	f
39	12	11	teste	2026-03-11 15:06:54.743425	f
40	5	4	vc lancou a paciente de amanha no cc? no mapa cirurgico?	2026-03-11 15:20:11.497585	f
41	4	5	Vou colocar agora	2026-03-11 15:36:06.863907	f
\.


--
-- Data for Name: commercial_task; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.commercial_task (id, patient_id, patient_name_snapshot, doctor_id, doctor_name_snapshot, consultation_id, source_type, planning_snapshot_json, total_value, status, priority, seller_notes, next_followup_date, last_contact_at, consultation_date, created_at, updated_at) FROM stdin;
44	13	LUANA	6	Dr. Vinicius	14	cp	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
45	293	DOUGLAS BRAGA TORRES BLANCA 	5	Dr. Arthur	337	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
46	13	LUANA	5	Dr. Arthur	16	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
47	234	SABRINA PELOSO	5	Dr. Arthur	267	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
48	119	manuela melani	5	Dr. Arthur	145	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
49	220	JOSEMAR VANZO	5	Dr. Arthur	252	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
50	168	NICOLAS NEGRI PEREIRA	5	Dr. Arthur	197	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
51	199	CLEVER ANGELO DE SOUZA 	5	Dr. Arthur	231	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
52	413	GUSTAVO CASTILHO SOARES	5	Dr. Arthur	486	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
53	347	CIBELE SIQUEIRA 	5	Dr. Arthur	402	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
54	296	ANDERSON SILVEIRA 	5	Dr. Arthur	340	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2023-05-03	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
55	76	GUSTAVO HENRIQUE SIGOLINE	5	Dr. Arthur	91	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
56	176	MATHEUS PELLA 	5	Dr. Arthur	205	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
57	262	FERNANDO ANTONIO MAURO PESSOA 	5	Dr. Arthur	300	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
58	160	MANUELA NEVES BORTOLO	5	Dr. Arthur	412	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
59	315	POLIANA MODA 	5	Dr. Arthur	359	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-01-28	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
60	341	ELIANE HADDAD	5	Dr. Arthur	396	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
61	318	WILHIAN KLEBER 	5	Dr. Arthur	363	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
62	129	GUSTAVO PEIXOTO MARTINS 	5	Dr. Arthur	155	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
63	106	VALDINEI MARCOS	5	Dr. Arthur	131	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
64	258	GUILHERME SANTOS 	5	Dr. Arthur	296	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
65	103	ALSONIA DE ANDRADE BARBOSA.	5	Dr. Arthur	126	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
66	50	DANIELA VELLUDO SPADONI	5	Dr. Arthur	65	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
67	283	ROSANA ALVES 	5	Dr. Arthur	326	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-02-26	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
68	405	VINICIUS ROCHA 	5	Dr. Arthur	474	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
69	305	FATIMA SOLANGE COSTA CAMPOS 	5	Dr. Arthur	349	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
70	310	RAFAEL LUIZ SPINA	5	Dr. Arthur	354	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
71	327	MARINA CILINO	5	Dr. Arthur	373	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
72	133	PEDRO GARCIA PALMA FIGUEIREDO	5	Dr. Arthur	160	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
73	302	ILLAN SALES GALVAO DE FIGUEIREDO	5	Dr. Arthur	346	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
74	242	JOSE RICARDO MINATEL	5	Dr. Arthur	275	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
75	130	ANA LIGIA SANTOS DE OLIVEIRA 	5	Dr. Arthur	156	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
76	240	ROSANA FARIA 	5	Dr. Arthur	273	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
77	241	RAFAEL NASCIMENTO CARIOLA 	5	Dr. Arthur	274	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
78	91	DAVI DELLA	5	Dr. Arthur	109	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
79	330	SARA SERAFIN LIMA	5	Dr. Arthur	377	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
80	97	ANDERSON ALEFANTE	5	Dr. Arthur	142	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
81	1	CAROLINA CARVALHO BASILE	5	Dr. Arthur	13	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
82	380	SILVIO MARTINS JUNIOR 	5	Dr. Arthur	442	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
83	191	NARIELLA MILHARI	5	Dr. Arthur	220	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
84	404	MARIA CELIA ZULIAN 	5	Dr. Arthur	473	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
85	24	WALTER BIAGI	5	Dr. Arthur	31	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
86	362	ANDREA GOMES PINTO 	5	Dr. Arthur	419	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
87	266	LUIZ ALEXANDRE PANINI 	5	Dr. Arthur	306	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
88	201	LUIS PAULO NASSIF FRANCISCO 	5	Dr. Arthur	233	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
89	127	CAMILA CAPARROTI DAL PICOLO ROTIROTI	5	Dr. Arthur	315	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
90	135	Antonio Cirne Salgado	5	Dr. Arthur	162	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
91	373	ANDREIA PINTO 	5	Dr. Arthur	432	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
92	182	ALESSANDRA RIPAMONTE	5	Dr. Arthur	425	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
93	96	CLAUDIA REGINA MONASSI KEDIA	5	Dr. Arthur	130	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
94	99	ROSELI GALVANI	5	Dr. Arthur	263	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
95	281	PEDRO GARCIA FERRAO 	5	Dr. Arthur	324	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
96	98	MARIA JOSE BASTO DA S. MATSUMOT	5	Dr. Arthur	119	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
97	245	NATALIA LETICIA TEIXEIRA ALVES 	5	Dr. Arthur	281	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
98	355	MARIA CRISTINA MAFUD 	7	Dr. Filipe	410	cp	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
99	48	LUCY APARECIDA DE OLIVEIRA	5	Dr. Arthur	115	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
100	203	CARLOS ROBERTO BUENO JUNIOR	5	Dr. Arthur	235	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
101	286	DANIEL DE JESUS BONFIM 	5	Dr. Arthur	329	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
102	106	VALDINEI MARCOS	5	Dr. Arthur	191	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
103	401	MILTON BORBA	5	Dr. Arthur	470	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
104	180	LILIANA CRUZ BIAGI SAID	5	Dr. Arthur	365	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
105	256	JOSE FONSECA NETO	5	Dr. Arthur	294	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
106	382	CAMILA DE BARROS MEIRELLES 	5	Dr. Arthur	446	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
107	150	MARCIO JUNIOR 	5	Dr. Arthur	177	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
108	65	CRISTIANI FAVARO GONÇALVES GAZONI	5	Dr. Arthur	80	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
109	222	ROXANA 	5	Dr. Arthur	254	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
110	27	TAISA MAGNANI	5	Dr. Arthur	34	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
111	289	GUSTAVO PASCHOAL	5	Dr. Arthur	333	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
112	195	FABIANA AZEVEDO 	5	Dr. Arthur	227	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
113	38	MARCELO EDUARDO LAMARCA PALENCIANO	5	Dr. Arthur	51	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
114	16	ANA MARIA AFONSO GEORGETE	5	Dr. Arthur	21	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
115	277	DENISE BALAN 	5	Dr. Arthur	318	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
116	139	ANTONIO BORGES 	5	Dr. Arthur	166	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
117	390	MARIA MARGARETH DENARDI BOSA	5	Dr. Arthur	455	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
118	7	RAFAEL FERNANDO ZAMBON	5	Dr. Arthur	35	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
119	123	MARIA EDUARDA S MIACHON 	5	Dr. Arthur	149	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
120	238	FRANCISCO CHIARELLO FERREIRA 	5	Dr. Arthur	271	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
121	247	ALCIDIA DE CASSIA 	5	Dr. Arthur	283	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
122	338	MARILIA DE CAMARGO BIASI 	5	Dr. Arthur	393	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
123	399	RICARDO VILELA SAID 	5	Dr. Arthur	466	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
124	174	RENATO VILELLA	5	Dr. Arthur	203	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
125	343	GUILHERME GRIFFO	5	Dr. Arthur	398	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
126	219	LEANDRO LUIZ DE ARAUJO LIMA ZAPAROLI 	5	Dr. Arthur	251	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
127	218	MARGARIDA SECCHES 	5	Dr. Arthur	250	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
128	153	CAIO AUGUSTO 	5	Dr. Arthur	180	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
129	386	RAMON WENDLER SILVA 	5	Dr. Arthur	450	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
130	125	PRISCILA G BRITO 	5	Dr. Arthur	151	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
131	375	MURILO NAZI ARNONI 	5	Dr. Arthur	434	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
132	276	RAFAEL VALERIO  ARANHA	5	Dr. Arthur	317	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
133	204	ENILSON JANUARIO	5	Dr. Arthur	236	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
134	40	PATRICIA CARVALHO UZUM	5	Dr. Arthur	54	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
135	136	PRISCILA PACHIONE 	5	Dr. Arthur	163	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
136	170	CARLOS ALBERTO TROVAO 	5	Dr. Arthur	199	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
137	377	FELIPE RANGEL 	5	Dr. Arthur	436	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
138	67	PALOMA DE KASSIA QUATRINI	5	Dr. Arthur	82	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
139	141	LUIS CARLOS STABILE 	5	Dr. Arthur	168	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
140	179	VANDERLENA LOT MARTINS	5	Dr. Arthur	208	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
141	322	MARISSON DONLEY WIEGUES	5	Dr. Arthur	368	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
142	263	LUIZ CARLOS PHEBER	5	Dr. Arthur	301	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
143	307	ROXANA CAZON ANGELO	5	Dr. Arthur	351	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-02-20	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
144	108	WILHIAN SANTOS	5	Dr. Arthur	133	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
145	21	JULIANA WEBBER CALDANA	5	Dr. Arthur	28	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
146	81	MARTA CONCEIÇAO TOSTA	5	Dr. Arthur	97	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
147	29	MANUELA RUIZ	5	Dr. Arthur	38	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
148	19	LAIS GONÇALVES BETINE	5	Dr. Arthur	26	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
149	9	TAUANE QUEIROZ	6	Dr. Vinicius	9	cp	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
150	87	MARIA APARECIDA BIANCHI	5	Dr. Arthur	105	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
151	161	SABRINA PAVAN VANZO BELEZA	5	Dr. Arthur	189	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
152	31	SILVIA BIAGI DINIZ JUNQUEIRA	6	Dr. Vinicius	41	cp	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
153	255	LUIS CARLOS 	5	Dr. Arthur	293	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
154	4	MARIA CRISTINA ALVES PEREIRA	6	Dr. Vinicius	4	cp	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
155	57	PATRICIA MARIA MONTANARI	5	Dr. Arthur	72	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
156	169	IRINEU JULIAO JUNIOR	5	Dr. Arthur	198	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
157	335	BRUNA RODRIGUES 	5	Dr. Arthur	382	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
158	37	LUCAS ALMEIDA COSTA	5	Dr. Arthur	50	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
159	216	HUGO CESAR DOJAS 	5	Dr. Arthur	248	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
160	64	MELINA PEDEZZI LANDI	5	Dr. Arthur	79	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
161	178	FRANCISCO ANTONIO	5	Dr. Arthur	207	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
162	243	JOSE CARLOS FORTES GUIMARAES 	5	Dr. Arthur	279	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
163	95	MARIA EUGENIA BORGES CONCEIÇAO	5	Dr. Arthur	225	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
164	110	NILSON MANHANI	5	Dr. Arthur	135	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
165	206	MARCELO MAMED ABDALLA 	5	Dr. Arthur	238	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
166	400	GUSTAVO AVILEZ MACRI 	5	Dr. Arthur	469	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
167	135	Antonio Cirne Salgado	5	Dr. Arthur	284	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
168	308	EMILIO CURY	5	Dr. Arthur	352	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
169	307	ROXANA CAZON ANGELO	5	Dr. Arthur	482	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
170	173	PEDRO DOMENCIANO 	5	Dr. Arthur	202	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
171	261	GIOVANNA FIORI	5	Dr. Arthur	299	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
172	138	OTAVIO PACHIONE 	5	Dr. Arthur	165	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
173	383	LUIS GUSTAVO TORRANO CORREA 	5	Dr. Arthur	447	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
174	339	PEDRO DOMENCIANO 	5	Dr. Arthur	394	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
175	227	ALEX AP MEDEIROS 	5	Dr. Arthur	259	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
176	188	SUZETE MAUCH PEREIRA 	5	Dr. Arthur	217	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
177	140	CLAUDIO INNOCENTE 	5	Dr. Arthur	167	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
178	219	LEANDRO LUIZ DE ARAUJO LIMA ZAPAROLI 	5	Dr. Arthur	463	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
179	63	WANIA CARLA MARTINS CORREA	5	Dr. Arthur	78	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
180	217	MILTON CARLOS C DE ALMEIDA PRADO	5	Dr. Arthur	249	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
181	349	ANTONIA GOIS DA SILVA DE MORAIS	7	Dr. Filipe	404	cp	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
182	246	LUIZ FERNANDO 	5	Dr. Arthur	282	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
183	80	SERGIO EDUARDO	5	Dr. Arthur	95	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
184	354	VALERIA GUAPO MACHADO 	7	Dr. Filipe	409	cp	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
185	70	EDNA BURRONE B. DO NASCIMENTO	5	Dr. Arthur	123	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
186	33	MAYARA MARINA MELO E GUIAO	5	Dr. Arthur	44	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
187	158	LUIZ GUSTAVO BACELAR	5	Dr. Arthur	185	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
188	61	POLLYANNA BOLINI MORETTI	5	Dr. Arthur	76	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
189	148	EUCLIDES BERNARDES 	5	Dr. Arthur	175	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
190	70	EDNA BURRONE B. DO NASCIMENTO	5	Dr. Arthur	85	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
191	71	MARY ARANTES WIERMANN BARROSO.	5	Dr. Arthur	86	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
192	364	SANDRA 	5	Dr. Arthur	421	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
193	185	OTAVIO AZEVEDO 	5	Dr. Arthur	214	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
194	223	GUILHERME MACHADO CAVALIERI 	5	Dr. Arthur	255	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
195	260	RENAN PEIXOTO 	5	Dr. Arthur	298	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
196	187	DIOGO ARROYO	5	Dr. Arthur	216	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
197	135	Antonio Cirne Salgado	5	Dr. Arthur	222	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
198	175	CLAUDIA SCHOLDEN	5	Dr. Arthur	454	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
199	62	ROSANA M MAGDALENA	5	Dr. Arthur	77	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
200	376	MANUELA NAZINI	5	Dr. Arthur	435	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
201	273	MELISSA SOARES 	5	Dr. Arthur	313	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
202	29	MANUELA RUIZ	6	Dr. Vinicius	37	cp	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
203	160	MANUELA NEVES BORTOLO	5	Dr. Arthur	187	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
204	143	CIBELE	5	Dr. Arthur	170	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
205	369	ADRIANO BRANDAO 	5	Dr. Arthur	427	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
206	48	LUCY APARECIDA DE OLIVEIRA	5	Dr. Arthur	62	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
207	239	ISABELLA SALGADO JUCATELLI	5	Dr. Arthur	303	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
208	224	MARIA ISABEL BIAGI DENADAI	5	Dr. Arthur	256	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
209	128	SUZETE MAUCH PEREIRA 	5	Dr. Arthur	154	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
210	111	ERIKA VENANCIO	5	Dr. Arthur	136	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
211	2	FERNANDA FERRARINI GOMES DA COSTA	5	Dr. Arthur	2	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
212	313	JOAO VITOR JARDIM DA SILVA 	5	Dr. Arthur	357	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
213	112	VANDER PAVAO	5	Dr. Arthur	137	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
214	232	LAURA MINTO 	5	Dr. Arthur	265	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
215	18	DEBORA MARIANO GOMES DA SILVA	5	Dr. Arthur	25	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
216	167	ENZO	5	Dr. Arthur	196	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
217	207	RAFAEL NOGUEIRA 	5	Dr. Arthur	239	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
218	104	LUCIANA ABEID RIBEIRO DALMAGRO	5	Dr. Arthur	128	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
219	357	GERLAINE 	5	Dr. Arthur	413	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
220	46	ANA FLAVIA MENDONÇA	5	Dr. Arthur	276	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
221	249	WALTER S JUNIOR 	5	Dr. Arthur	286	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
222	34	LARA FERRAZ.	5	Dr. Arthur	45	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
223	344	JULIANA PRADELA	5	Dr. Arthur	399	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
224	137	OLIVIA PACHIONE 	5	Dr. Arthur	164	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
225	1	CAROLINA CARVALHO BASILE	5	Dr. Arthur	1	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
226	213	RAFAEL CARIOLA 	5	Dr. Arthur	245	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
227	73	MARIA DO CARMO ANTONIALLI MARINO	5	Dr. Arthur	88	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
228	93	MARCIO CUSTODIO DA SILVA	5	Dr. Arthur	111	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
229	74	MAIRA FREY RIFFEL	5	Dr. Arthur	89	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
230	82	FABIOLA MOREIRA ANDRADE	5	Dr. Arthur	99	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
231	151	JOSE RUBENS FURTADO 	5	Dr. Arthur	178	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
232	393	ROSANA CASTELLI	5	Dr. Arthur	458	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
233	92	JOSE ADEMIR FERRAO	5	Dr. Arthur	110	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
234	102	ANDERSON MOREIRA ZANON TENORIO	5	Dr. Arthur	125	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
235	372	ANDREIA PINTO 	5	Dr. Arthur	431	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
236	56	HENRIQUE CANDIA VICENTE AZEVEDO	5	Dr. Arthur	71	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
237	332	BRUNO BATAER	5	Dr. Arthur	379	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
238	49	VALDACIRA AP GUARNIERI	5	Dr. Arthur	64	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
239	351	ROSEMAR DE SOUZA SILVA	7	Dr. Filipe	406	cp	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
240	126	ANTONIO JACINTHO GUIMARAES 	5	Dr. Arthur	152	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
241	124	CRISLAINE JAMARINO 	5	Dr. Arthur	150	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
242	274	NEUZA MARIA REIS DE ALMEIDA 	5	Dr. Arthur	314	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
243	165	MICHELE SERANTOLA 	5	Dr. Arthur	194	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
244	72	WILIAN CAMARGO DA COSTA	5	Dr. Arthur	87	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
245	238	FRANCISCO CHIARELLO FERREIRA 	5	Dr. Arthur	443	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
246	1	CAROLINA CARVALHO BASILE	5	Dr. Arthur	98	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
247	77	SILMARA PADOVAN SPAZIANE	5	Dr. Arthur	92	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
248	346	WALTER BALBI	5	Dr. Arthur	401	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
249	40	PATRICIA CARVALHO UZUM	5	Dr. Arthur	53	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
250	164	DIEGO SANTOS 	5	Dr. Arthur	193	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
251	299	CLAUDIO INNOCENTE 	5	Dr. Arthur	343	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
252	314	ALEXANDRA CRISTINA BARBOSA 	5	Dr. Arthur	358	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-01-21	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
253	297	MARCIA NASSUR 	5	Dr. Arthur	341	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-02-27	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
254	387	ISABELLA SUHADOLNIK MAIA BARBOSA 	5	Dr. Arthur	451	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
255	215	FERNANDO HENRIQUE MARQEUS DE VICENTE 	5	Dr. Arthur	247	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
256	36	RITA DE CASSIA ALCIDES	5	Dr. Arthur	49	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
257	226	LUIZA ARROYO DE ALMEIDA PRADO	5	Dr. Arthur	258	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
258	62	ROSANA M MAGDALENA	5	Dr. Arthur	321	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
259	181	GUILHERMINA RIPAMONTE 	5	Dr. Arthur	210	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
260	96	CLAUDIA REGINA MONASSI KEDIA	5	Dr. Arthur	114	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
261	252	GUSTAVO MAGALAHES 	5	Dr. Arthur	289	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
262	152	JOICE AP QUINTINO 	5	Dr. Arthur	179	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
263	54	ADRIANA APARECIDA MELO.	5	Dr. Arthur	120	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
264	208	YURI FIRMINO	5	Dr. Arthur	240	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
265	11	EDUARDO DE BARROS CORREIA	5	Dr. Arthur	23	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
266	8	JOAO PAULO EUGENIO DA SILVA	6	Dr. Vinicius	8	cp	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
267	397	JULIA CALSAROLI 	5	Dr. Arthur	462	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
268	368	ERNANE DONIZETE	5	Dr. Arthur	426	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
269	52	IURI SVERZUT BELLESINI	5	Dr. Arthur	67	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
270	117		5	Dr. Arthur	143	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
271	177	FRANCISCO CHIARELLO FERREIRA 	5	Dr. Arthur	206	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
272	200	GABRIEL DANEZZI 	5	Dr. Arthur	232	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
273	85	JULIANA BENASSI SANTON.	5	Dr. Arthur	102	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
274	292	MARCELO DANILO ZANFRILLE 	5	Dr. Arthur	336	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
275	183	EMILSON JANUARIO	5	Dr. Arthur	212	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
276	182	ALESSANDRA RIPAMONTE	5	Dr. Arthur	211	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
277	171	ALEXANDRE VINICIUS DA SILVA PEREIRA 	5	Dr. Arthur	200	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
278	326	JULIA FONTANETTI	5	Dr. Arthur	372	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
279	89	PAULO CESAR AP CINTRA	5	Dr. Arthur	107	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
280	78	JULIANA CRISTINA SPAZIANI PANE.	5	Dr. Arthur	96	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
281	202	LUIS PAULO NASSIF FRANCISCO 	5	Dr. Arthur	234	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
282	61	POLLYANNA BOLINI MORETTI	5	Dr. Arthur	476	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
283	407	MARIA EDUARDA VANZO	5	Dr. Arthur	478	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
284	367	MARCIUS SIERRO DIAS 	5	Dr. Arthur	424	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
285	155	ADIMARIS GABRIELA RONCADA	5	Dr. Arthur	182	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
286	378	EVILYN MARIA COLANGELO 	5	Dr. Arthur	439	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
287	221	JULIA CALSAROLI 	5	Dr. Arthur	253	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
288	93	MARCIO CUSTODIO DA SILVA	5	Dr. Arthur	437	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
289	157	VICTOR GASPARINI 	5	Dr. Arthur	184	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
290	229	CAMILA UBIDA	5	Dr. Arthur	261	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
291	26	SOPHIA CIMATTI BELENTANI	5	Dr. Arthur	33	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
292	80	SERGIO EDUARDO	5	Dr. Arthur	104	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
293	17	ADRIANA DA SILVA.	5	Dr. Arthur	22	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
294	196	ESDRAS SILVA 	5	Dr. Arthur	228	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
295	324	ISADORA GOMES 	5	Dr. Arthur	430	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
296	229	CAMILA UBIDA	5	Dr. Arthur	392	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
297	105	LUCIANA FINOTO MELO	5	Dr. Arthur	291	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
298	301	SANDRA MARCIA FERRAO ZAPOLLA	5	Dr. Arthur	345	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
299	120	ALLAN RICARDO CARUSO 	5	Dr. Arthur	146	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
300	101	LAERCIO ERNESTO DE SOUZA	5	Dr. Arthur	124	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
301	39	HUGO BRANQUINHO DE CARVALHO	5	Dr. Arthur	52	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
302	336	luciana pimenta mattos	7	Dr. Filipe	383	cp	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
303	97	ANDERSON ALEFANTE	5	Dr. Arthur	117	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
304	325	EDUARDO HENRIQUE GOMES 	5	Dr. Arthur	371	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
305	14	ALEXANDRE	6	Dr. Vinicius	15	cp	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
306	233	OSVALDO OSSANO 	5	Dr. Arthur	266	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
307	20	FERNANDES DIAS DE SOUZA	5	Dr. Arthur	27	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
308	323	ANDREIA PINTO 	5	Dr. Arthur	369	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
309	406	LUIS ALBERTO	5	Dr. Arthur	475	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
310	46	ANA FLAVIA MENDONÇA	5	Dr. Arthur	60	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
311	184	RENAN ANTUNES CONTE 	5	Dr. Arthur	213	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
312	244	JOVITA MADALENA ALVES MORENO	5	Dr. Arthur	280	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
313	316	SUZETE MAUCH PEREIRA 	5	Dr. Arthur	360	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-01-26	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
314	359	LUCAS DANIEL 	5	Dr. Arthur	415	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
315	306	CARLOS ALBERTO TROVAO 	5	Dr. Arthur	350	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
316	51	JESSICA MAGANHA	5	Dr. Arthur	66	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
317	186	OLIVIA AZEVEDO 	5	Dr. Arthur	215	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
318	328	MARCILENE APARECIDA GONÇALVES 	5	Dr. Arthur	375	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2025-11-27	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
319	100	MARCELO C. TAZINAFFO	5	Dr. Arthur	122	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
320	149	RAFAELA MAGNANI DINAMARCO.	5	Dr. Arthur	176	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
321	248	MARTA RODRIGUES MAFEIS 	5	Dr. Arthur	285	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
322	268	MARIANA FRANÇA BAYEUX POTENZA 	5	Dr. Arthur	308	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
323	284	RAFAEL COLICCHIO	5	Dr. Arthur	327	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
324	31	SILVIA BIAGI DINIZ JUNQUEIRA	6	Dr. Vinicius	40	cp	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
325	94	BRUNA BETTIOL ORTEIRO	5	Dr. Arthur	112	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
326	391	ALESSANDRA AP BIDO RIBEIRO	5	Dr. Arthur	456	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
327	163	LAURA DE CACERES SOUZA 	5	Dr. Arthur	192	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
328	385	GABRIEL DANEZZI 	5	Dr. Arthur	449	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
329	63	WANIA CARLA MARTINS CORREA	5	Dr. Arthur	118	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
330	237	ROBERVAL CARVALHO JUNIOR.	5	Dr. Arthur	270	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
331	122	NILSON CARLOS MANHANI	5	Dr. Arthur	148	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
332	212	CARMEN SILVA 	5	Dr. Arthur	244	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
333	230	GUILHERME 	5	Dr. Arthur	262	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
334	109	BRUNO CESAR LEDO	5	Dr. Arthur	134	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
335	79	ELIANE R HADDAD	5	Dr. Arthur	94	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
336	287	APARECIDA DONIZETE 	5	Dr. Arthur	330	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
337	5	SHIRLEY MARLENE DE SOUZA	6	Dr. Vinicius	5	cp	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
338	253	JOSEANE	5	Dr. Arthur	290	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
339	403	MARINA GARCIA HECK	5	Dr. Arthur	472	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
340	54	ADRIANA APARECIDA MELO.	5	Dr. Arthur	69	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
341	59	SABIE AP.CALIL TANNUS	5	Dr. Arthur	74	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
342	317	CACILDA SANTIAGO 	5	Dr. Arthur	362	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-02-02	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
343	319	JULIANA SANTANA 	5	Dr. Arthur	364	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
344	291	DENISE BALDAN	5	Dr. Arthur	335	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
345	363	ANNA KARINA BOLINI	5	Dr. Arthur	420	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
346	356	MARIA DARCY TEIXEIRA A. SIQUEIRA	5	Dr. Arthur	411	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
347	31	SILVIA BIAGI DINIZ JUNQUEIRA	5	Dr. Arthur	42	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
348	259	DANIELE BIAGI	5	Dr. Arthur	361	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
349	311	JOAO VICTOR SOMERA 	5	Dr. Arthur	355	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
350	332	BRUNO BATAER	5	Dr. Arthur	438	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
351	264	MARCILENE APARECIDA GONÇALVES 	5	Dr. Arthur	304	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
352	396	ROSANJO SOUZA 	5	Dr. Arthur	461	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
353	363	ANNA KARINA BOLINI	5	Dr. Arthur	477	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
354	69	CARLOS JOSE PEREIRA	5	Dr. Arthur	84	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
355	15	ARISLILIAN RAGOZONE CONRADO	5	Dr. Arthur	19	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
356	10	LEANDRO FELICIO NEVES	5	Dr. Arthur	10	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
357	95	MARIA EUGENIA BORGES CONCEIÇAO	5	Dr. Arthur	113	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
358	115	GEANE ESTELA AKOS	5	Dr. Arthur	140	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
359	114	RAFAEL MANFRIN CONEGLIAN	5	Dr. Arthur	139	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
360	304	GUILHERME OLIVEIRA 	5	Dr. Arthur	348	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
361	84	LIVIA GALVANI DE BARROS CRUZ.	5	Dr. Arthur	101	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
362	394	LUCIENE CASTELLI	5	Dr. Arthur	459	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
363	41	ROGILSON	5	Dr. Arthur	55	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
364	90	HERIKA CARDOSO LEITE	5	Dr. Arthur	108	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
365	324	ISADORA GOMES 	5	Dr. Arthur	370	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
366	408	LETICIA FABBRI	5	Dr. Arthur	479	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
367	1	CAROLINA CARVALHO BASILE	5	Dr. Arthur	48	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
368	279	LUCCA TORRANO FREDERICO CORREA 	5	Dr. Arthur	320	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
369	280	LENNON FLAVIO	5	Dr. Arthur	323	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
370	214	OTAVIO PACHIONE 	5	Dr. Arthur	246	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
371	99	ROSELI GALVANI	5	Dr. Arthur	121	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
372	205	MARCIO SAULO DE MELLO MARTINS JR	5	Dr. Arthur	237	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
373	113	SEFORAH MARINA PACIFICO MANFRIM CONEGLIAN	5	Dr. Arthur	138	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
374	197	HELENA ABUD 	5	Dr. Arthur	229	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
375	231	ROSSI	5	Dr. Arthur	264	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
376	348	ANA LUISA TENORI	7	Dr. Filipe	403	cp	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
377	366	JOSE SAMUEL 	5	Dr. Arthur	423	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
378	388	RAISSA FRANCIELE 	5	Dr. Arthur	452	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
379	172	JOSE MAURICIO AGUIAR JUNIOR 	5	Dr. Arthur	201	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
380	156	JULIANA SANTANA 	5	Dr. Arthur	183	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
381	290	GABRIELA BENEDINE 	5	Dr. Arthur	334	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
382	324	ISADORA GOMES 	5	Dr. Arthur	418	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
383	352	IVANI CARLA OMETTO	7	Dr. Filipe	407	cp	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
384	43	MARIA CRISTINA ALVES PEREIRA.	5	Dr. Arthur	57	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
385	134	EVA GOMES 	5	Dr. Arthur	161	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
386	42	EDUARDO KAZUO	5	Dr. Arthur	56	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
387	145	DENISE BALAN 	5	Dr. Arthur	172	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
388	337	RENATA CHIARELLO PEREIRA 	5	Dr. Arthur	391	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
389	270	BRUNA TUCCI SANTIAGO	5	Dr. Arthur	310	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
390	269	DENISE BALAN 	5	Dr. Arthur	309	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
391	14	ALEXANDRE	5	Dr. Arthur	17	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
392	257	MAURO COLICCHIO	5	Dr. Arthur	295	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
393	1	CAROLINA CARVALHO BASILE	5	Dr. Arthur	116	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
394	45	LIVIA PIOLI NAILS	5	Dr. Arthur	59	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
395	334	RAFAEL FURTADO CARLOS DE OLIVEIRA 	5	Dr. Arthur	381	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
396	321	BRANCA MEIRELLES 	5	Dr. Arthur	367	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
397	265	CARLOS ROBERTO MARQUES JUNIOR 	5	Dr. Arthur	305	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
398	329	JANDIMILIA	5	Dr. Arthur	376	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
399	74	MAIRA FREY RIFFEL	5	Dr. Arthur	157	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
400	340	ADILSON HADDAD	5	Dr. Arthur	395	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
401	381	DENIS GUSTAVO MORENO	5	Dr. Arthur	444	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2025-02-17	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
402	18	DEBORA MARIANO GOMES DA SILVA	6	Dr. Vinicius	24	cp	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
403	211	ROBERTO MARTINS	5	Dr. Arthur	243	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
404	105	LUCIANA FINOTO MELO	5	Dr. Arthur	129	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
405	250	ROSANO SOUZA 	5	Dr. Arthur	287	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
406	159	CAROLINA NAKANO FURTADO STRANG	5	Dr. Arthur	186	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
407	190	JONAS RICARDO 	5	Dr. Arthur	219	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
408	88	MARIA AUGUSTA BIANCHI	5	Dr. Arthur	106	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
409	11	EDUARDO DE BARROS CORREIA	5	Dr. Arthur	47	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
410	365	SHAOYAN CHEN	5	Dr. Arthur	422	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
411	49	VALDACIRA AP GUARNIERI	5	Dr. Arthur	278	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
412	23	RODRIGO VILELA	5	Dr. Arthur	30	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
413	132	MARINA MARCUZZO DA CRUZ 	5	Dr. Arthur	159	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
414	379	RENATO CESAR STELLA	5	Dr. Arthur	440	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2025-02-18	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
415	294	JOAQUIM FOLIETE SANTOS 	5	Dr. Arthur	338	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
416	75	DOUGLAS FIOCHIO	5	Dr. Arthur	90	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
417	198	HUGO FRONZAGLIA	5	Dr. Arthur	230	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
418	410	JOAO PEDRO 	5	Dr. Arthur	483	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
419	324	ISADORA GOMES 	5	Dr. Arthur	429	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
420	307	ROXANA CAZON ANGELO	5	Dr. Arthur	374	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
421	175	CLAUDIA SCHOLDEN	5	Dr. Arthur	416	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
422	25	PATRICIA HOPP	5	Dr. Arthur	32	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
423	225	GISELE CRISTINA DE ARAUJO 	5	Dr. Arthur	467	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
424	192	ANTONIO BORGES 	5	Dr. Arthur	221	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
425	142	DEIVED DOUGLAS GUARNIERI	5	Dr. Arthur	169	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
426	411	RAFAEL DE CARVALHO NOGUEIRA 	5	Dr. Arthur	484	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
427	118	MARCO AURELIO BERNARDO	5	Dr. Arthur	144	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
428	409	ANA MARIA BIAGI	5	Dr. Arthur	481	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
429	127	CAMILA CAPARROTI DAL PICOLO ROTIROTI	5	Dr. Arthur	153	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
430	35	ALICE SANCHES ALMEIDA14/08/2014	5	Dr. Arthur	46	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
431	175	CLAUDIA SCHOLDEN	5	Dr. Arthur	204	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
432	131	FABIANO GALVAO 	5	Dr. Arthur	158	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
433	320	ANA LIGIA SANTOS DE OLIVEIRA 	5	Dr. Arthur	366	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-02-02	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
434	225	GISELE CRISTINA DE ARAUJO 	5	Dr. Arthur	257	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
435	32	LAYLLA CRISTHINE DE ALMEIDA REZENDE	5	Dr. Arthur	43	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
436	47	JACIRA GUARNIERI	5	Dr. Arthur	61	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
437	121	ISABEL CRISTINA DE SOUSA MIACHON.	5	Dr. Arthur	147	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
438	116	AMANDA BARBOSA	5	Dr. Arthur	141	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
439	398	FABIO ALEXANDRE CARNEIRO 	5	Dr. Arthur	464	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
440	144	ALVARO GARBINI	5	Dr. Arthur	171	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
441	358	NEUZA MARIA REIS DE ALMEIDA 	5	Dr. Arthur	414	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
442	333	BRUNA GABRIELA MONTAGNANI	5	Dr. Arthur	380	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
443	267	GABRIEL BAYAX POTENZA 	5	Dr. Arthur	307	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
444	285	SILVANA COLICCHIO	5	Dr. Arthur	328	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
445	309	FELIPE RUSSO 	5	Dr. Arthur	353	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-02-02	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
446	103	ALSONIA DE ANDRADE BARBOSA.	5	Dr. Arthur	302	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
447	28	CASSIO FLORIANO	5	Dr. Arthur	36	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
448	395	CLEITON DIAS 	5	Dr. Arthur	460	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
449	44	RENAN BECKER	5	Dr. Arthur	58	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
450	47	JACIRA GUARNIERI	5	Dr. Arthur	277	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
451	58	LAURA LETICIA PEREZ BECK	5	Dr. Arthur	73	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
452	331	MARISSON DONLEY WIRGUES	5	Dr. Arthur	378	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
453	162	SOLANGE RODRIGUES BARBOSA 	5	Dr. Arthur	190	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
454	342	DORAMA MODA 	5	Dr. Arthur	397	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
455	22	ROBERTA DE OLIVEIRA MARIANO	5	Dr. Arthur	29	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
456	288	MARIA VICTORIA 	5	Dr. Arthur	331	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
457	105	LUCIANA FINOTO MELO	5	Dr. Arthur	445	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
458	259	DANIELE BIAGI	5	Dr. Arthur	441	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
459	389	EUCLIDES BERNARDES 	5	Dr. Arthur	453	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
460	392	DANILO PANTALEAO MARÇAL 	5	Dr. Arthur	457	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
461	118	MARCO AURELIO BERNARDO	5	Dr. Arthur	188	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
462	278	MARCIO LUIS MARTINS 	5	Dr. Arthur	319	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
463	298	CRISLAINE JAMARINO 	5	Dr. Arthur	342	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
464	189	DENIS CRISTIANO JORA 	5	Dr. Arthur	218	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
465	345	EUCLIDES BERNARDES 	5	Dr. Arthur	400	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
466	83	ERIKA VILLAR S. FORTES GUIMARAES	5	Dr. Arthur	100	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
467	60	SUELEN APARECIDA DACANAL DE SOUSA	5	Dr. Arthur	75	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
468	6	LUIS HENRIQUE RONCARI JUNIOR	6	Dr. Vinicius	6	cp	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
469	254	SERGIO NUNES	5	Dr. Arthur	292	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
470	360	CLEBER ROBERTO VIOLIN	5	Dr. Arthur	417	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
471	55	REGINALDO MARQUES	5	Dr. Arthur	70	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
472	295	THAISA MARIA VELLASCO QUEIROZ PIMENTA. 	5	Dr. Arthur	339	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
473	107	PEDRO ROBERTO	5	Dr. Arthur	132	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
474	235	FERNANDO MORETTO	5	Dr. Arthur	268	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
475	30	MARCELO MINIKOWSKI	5	Dr. Arthur	39	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
476	210	BRUNO MULATO 	5	Dr. Arthur	242	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
477	353	THAIS 	7	Dr. Filipe	408	cp	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
478	147	FELIPE  RUSSO 	5	Dr. Arthur	174	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
479	78	JULIANA CRISTINA SPAZIANI PANE.	5	Dr. Arthur	93	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
480	220	JOSEMAR VANZO	5	Dr. Arthur	468	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
481	282	LUANA BOSCHETI	5	Dr. Arthur	325	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
482	224	MARIA ISABEL BIAGI DENADAI	5	Dr. Arthur	480	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
483	135	Antonio Cirne Salgado	5	Dr. Arthur	465	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
484	307	ROXANA CAZON ANGELO	5	Dr. Arthur	428	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
485	86	MARCIA CRISTINA GUEDES JANUARIO	5	Dr. Arthur	103	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
486	228	PEDRO SIMATI	5	Dr. Arthur	260	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
487	66	LUIS CARLOS GONÇALVES.	5	Dr. Arthur	81	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
488	194	JOSE MATHEUS 	5	Dr. Arthur	226	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
489	3	RENATO ZUPPANI	6	Dr. Vinicius	3	cp	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
490	275	VERA GARCIA	5	Dr. Arthur	316	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
491	350	DANI 	7	Dr. Filipe	405	cp	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
492	239	ISABELLA SALGADO JUCATELLI	5	Dr. Arthur	272	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
493	236	MATHEUS PELLA 	5	Dr. Arthur	269	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
494	374	SUELI GOTARDI MOITINHO.	5	Dr. Arthur	433	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
495	68	LIVIA CALUZ ULIAN	5	Dr. Arthur	83	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
496	384	CRISLAINE JAMARINO 	5	Dr. Arthur	448	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
497	166	GUILHERME OLIVEIRA 	5	Dr. Arthur	195	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
498	251	JULIANNA 	5	Dr. Arthur	288	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
499	412	ROBERTO AUDE JABALI 	5	Dr. Arthur	485	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
500	180	LILIANA CRUZ BIAGI SAID	5	Dr. Arthur	209	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
501	209	CLAYTON SALLES	5	Dr. Arthur	241	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
502	402	HENRIQUE CROSIO FILHO	5	Dr. Arthur	471	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
503	271	WILHIAN MONASSI	5	Dr. Arthur	311	derma	{"items": [], "nota": ""}	0.00	novo	media	\N	\N	\N	2026-03-12	2026-03-12 12:54:38.854822	2026-03-12 12:54:38.854822
\.


--
-- Data for Name: cosmetic_procedure_plan; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.cosmetic_procedure_plan (id, note_id, procedure_name, planned_value, final_budget, was_performed, performed_date, follow_up_months, created_at, observations) FROM stdin;
1	3	Botox	1200.00	1200.00	t	2025-11-25 00:00:00	6	2025-11-25 18:52:40.630315	
2	3	Preenchimento	1250.00	1250.00	t	2025-11-25 00:00:00	6	2025-11-25 18:52:40.723023	
3	3	Ulthera	5000.00	5000.00	f	\N	6	2025-11-25 18:52:40.811358	
4	10	Botox	1200.00	1200.00	t	2025-11-27 00:00:00	6	2025-11-27 23:02:34.037748	
5	10	Sculptra	5000.00	5000.00	t	2025-11-27 00:00:00	6	2025-11-27 23:02:34.137891	
6	10	Profhilo	2000.00	2000.00	f	\N	6	2025-11-27 23:02:34.224019	Colo
7	14	Botox	1200.00	1200.00	t	2025-11-28 00:00:00	6	2025-11-28 19:52:12.33144	
8	14	Ulthera	4000.00	4000.00	t	2025-11-28 00:00:00	6	2025-11-28 19:52:12.471814	
9	20	Botox	1200.00	1200.00	f	\N	6	2025-12-02 12:51:15.121372	
10	20	Peeling	1000.00	1000.00	f	\N	6	2025-12-02 12:51:15.22222	limeght face
11	23	Botox	1200.00	1200.00	t	2025-12-02 00:00:00	6	2025-12-02 13:03:31.930977	
12	28	Botox	1200.00	1200.00	t	2025-12-02 00:00:00	6	2025-12-02 14:01:24.590953	
13	28	Sculptra	5000.00	5000.00	f	\N	6	2025-12-02 14:01:24.684962	
14	30	Botox	1100.00	1100.00	t	2025-12-02 00:00:00	6	2025-12-02 19:30:47.264339	
15	34	Botox	600.00	1200.00	t	2025-12-03 00:00:00	6	2025-12-03 18:47:43.622498	nefertiti
16	34	Morpheus	6000.00	6000.00	f	\N	6	2025-12-03 18:47:43.716751	fae e papada
17	40	Preenchimento	1250.00	1250.00	t	2025-12-04 00:00:00	6	2025-12-04 17:16:19.426167	contorno 1-2 ampolas 
18	40	Ulthera	3000.00	3000.00	f	\N	6	2025-12-04 17:16:19.522684	meia face _ olhos e se for fazer so papadinha mais 1000
19	40	Botox	1100.00	1100.00	f	\N	6	2025-12-04 17:16:19.612245	
20	50	Morpheus	6000.00	6000.00	f	\N	6	2025-12-05 13:28:35.444134	face 1x/ano
21	50	Preenchimento	10000.00	10000.00	f	\N	6	2025-12-05 13:28:35.540451	preecnhimento gluteo 2 ampolas no minimo 10ml
22	55	Botox	1100.00	1100.00	t	2025-12-09 00:00:00	6	2025-12-09 18:10:25.476298	
23	55	Morpheus	6000.00	6000.00	f	\N	6	2025-12-09 18:10:25.575461	indico face e pescoco  m,as so quer face adicionar anestesista
24	57	Botox	1000.00	1000.00	t	2025-12-09 00:00:00	6	2025-12-09 18:17:21.048304	face
25	59	Botox	1100.00	1100.00	t	2025-12-09 00:00:00	6	2025-12-09 19:09:48.620247	
26	59	Radiesse	2000.00	2000.00	f	\N	6	2025-12-09 19:09:48.713455	1 ampola
27	61	Sculptra	5000.00	5000.00	f	\N	6	2025-12-09 19:16:08.229017	gluteo
28	67	Preenchimento	1500.00	1500.00	t	2025-12-09 00:00:00	6	2025-12-09 20:34:20.897263	queixo e ck1 eshape
29	70	Botox	1200.00	1200.00	t	2025-12-09 00:00:00	6	2025-12-09 20:53:49.424733	
30	70	Preenchimento	2500.00	2500.00	t	2025-12-09 00:00:00	6	2025-12-09 20:53:49.502909	2 ampolas sulco nasogeninao
31	72	Botox	1.00	1.00	t	2025-12-10 00:00:00	6	2025-12-10 17:52:32.731966	
32	82	Botox	1100.00	1100.00	t	2025-12-11 00:00:00	6	2025-12-11 12:04:07.850643	
33	82	Preenchimento	2500.00	2500.00	t	2025-12-11 00:00:00	6	2025-12-11 12:04:07.947091	1 renova labios 0,8 labios e 0,4 nariz 1 voluma c1 0,6 e 0,4 sulco
34	88	Botox	1100.00	1100.00	t	2025-12-11 00:00:00	5	2025-12-11 12:35:39.320324	
35	96	Botox	1200.00	1200.00	t	2025-12-11 00:00:00	6	2025-12-11 15:16:38.726178	
36	96	Preenchimento	1300.00	1300.00	t	2025-12-11 00:00:00	6	2025-12-11 15:16:38.833888	RENOVA LIFT O,2ML SULCO DIREITO E CK1 CK2
37	96	Morpheus	6000.00	6000.00	f	\N	4	2025-12-11 15:16:38.924507	6000 PACOTE COM 3 MORPHEUS PALPEBRA
38	98	Botox	1100.00	1100.00	t	2025-12-11 00:00:00	6	2025-12-11 17:59:53.803206	
39	98	Ulthera	4000.00	4000.00	f	\N	6	2025-12-11 17:59:53.803222	face
40	100	Botox	1100.00	1100.00	t	2025-12-11 00:00:00	6	2025-12-11 18:33:23.086047	
41	100	Morpheus	8000.00	8000.00	f	\N	6	2025-12-11 18:33:23.086061	indico morpheus face mais pdrn e ate limght para melhorar as manchas
42	102	Botox	1200.00	1200.00	t	2025-12-11 00:00:00	6	2025-12-11 19:19:03.048085	
43	102	Morpheus	18000.00	18000.00	f	\N	6	2025-12-11 19:19:03.0481	face pesococo  e limeght para manchas antes cobrar anestesista a parte
44	104	Botox	1100.00	1100.00	t	2025-12-12 00:00:00	5	2025-12-12 12:41:57.637567	
45	104	Ulthera	4000.00	4000.00	f	\N	6	2025-12-12 12:41:57.637582	face
46	104	Outros	2500.00	2500.00	f	\N	10	2025-12-12 12:41:57.637586	skinbooster
47	106	Botox	1100.00	1100.00	t	2025-12-12 00:00:00	6	2025-12-12 12:57:43.901448	
48	106	Preenchimento	1250.00	1250.00	t	2025-12-12 00:00:00	6	2025-12-12 12:57:43.901469	usei balance sulco pior a direita
49	110	Botox	1100.00	1100.00	t	2025-12-12 00:00:00	6	2025-12-12 14:08:04.291176	masseter
50	112	Botox	2400.00	2400.00	f	\N	6	2025-12-12 17:36:36.773835	botox normal e masseter
51	114	Botox	1100.00	1100.00	t	2025-12-12 00:00:00	5	2025-12-12 18:56:35.44835	
52	114	Sculptra	2500.00	2500.00	f	\N	6	2025-12-12 18:56:35.448364	1 a 2 ampolas
53	116	Botox	1100.00	1100.00	t	2025-12-12 00:00:00	6	2025-12-12 18:56:58.268106	
54	118	Botox	1200.00	1200.00	t	2025-12-12 00:00:00	6	2025-12-12 19:56:09.382641	
55	118	Morpheus	6000.00	6000.00	f	\N	6	2025-12-12 19:56:09.382656	face e pescoco
56	122	Botox	1200.00	1200.00	t	\N	6	2025-12-12 20:17:35.409134	
57	122	Sculptra	5000.00	5000.00	t	\N	6	2025-12-12 20:17:35.409158	
58	122	Profhilo	2000.00	2000.00	t	2025-12-12 00:00:00	6	2025-12-12 20:17:35.409166	
59	122	Sculptra	5000.00	5000.00	t	2025-12-12 00:00:00	12	2025-12-12 20:17:35.409172	gluteo
60	124	Preenchimento	2500.00	2500.00	t	2025-12-15 00:00:00	6	2025-12-15 13:18:40.178238	renova lift ck1 ck2 e 0,2 no labio superior e por assimetria, volbela labios para hidratacao
61	131	Ulthera	4000.00	4000.00	f	\N	6	2025-12-15 13:35:58.344975	
62	131	Outros	1800.00	1800.00	f	\N	6	2025-12-15 13:35:58.344996	exerese de dermatofibroma maos direita 
63	134	Ulthera	4000.00	4000.00	f	\N	6	2025-12-15 13:42:15.484343	
64	134	Outros	1800.00	1800.00	f	\N	6	2025-12-15 13:42:15.484355	exerese de lesao dermatofibroma na mao  direita
65	138	Botox	1100.00	1100.00	t	2025-12-15 00:00:00	6	2025-12-15 14:21:11.427269	
66	142	Botox	1100.00	1100.00	t	2025-12-15 00:00:00	6	2025-12-15 18:58:15.302269	
67	142	Morpheus	6000.00	6000.00	f	\N	6	2025-12-15 18:58:15.302291	face
68	144	Botox	1100.00	1100.00	t	2025-12-15 00:00:00	6	2025-12-15 20:03:59.824574	
69	146	Botox	1200.00	1200.00	t	2025-12-16 00:00:00	6	2025-12-16 14:00:58.003025	
70	146	Pearl Fracionado	2500.00	2500.00	t	2025-08-29 00:00:00	6	2025-12-16 14:00:58.003061	
71	146	Sculptra	2500.00	2500.00	t	2025-08-29 00:00:00	6	2025-12-16 14:00:58.003068	
72	148	Botox	1200.00	1200.00	t	2025-12-16 00:00:00	6	2025-12-16 18:32:45.101398	
73	148	Botox	1200.00	1200.00	f	\N	6	2025-12-16 18:32:45.101422	masseter
74	150	Sculptra	5000.00	5000.00	f	\N	6	2025-12-17 14:07:04.497249	
75	150	Sculptra	5000.00	5000.00	t	2025-12-17 00:00:00	6	2025-12-17 14:07:04.49727	elleva x gluteos
76	150	Preenchimento	10000.00	10000.00	t	2025-12-17 00:00:00	6	2025-12-17 14:07:04.497277	sofiderm 20 ml
77	152	Botox	1100.00	1100.00	t	2026-01-19 00:00:00	4	2026-01-19 17:26:46.593025	
78	152	Pearl Fracionado	3000.00	3000.00	f	\N	6	2026-01-19 17:26:46.593042	
79	154	Botox	1100.00	1100.00	t	\N	6	2026-01-19 17:41:19.095421	
80	154	Preenchimento	2500.00	2500.00	t	\N	6	2026-01-19 17:41:19.095445	
81	156	Botox	900.00	900.00	t	2026-01-19 00:00:00	6	2026-01-19 18:54:20.295469	
82	158	Botox	1200.00	1200.00	t	2026-01-19 00:00:00	6	2026-01-19 18:55:09.546995	
83	160	Botox	1100.00	1100.00	t	\N	6	2026-01-19 19:40:37.006033	
84	160	Ulthera	4000.00	4000.00	t	2026-01-19 00:00:00	6	2026-01-19 19:40:37.00605	
85	162	Botox	1200.00	1200.00	t	2026-01-21 00:00:00	6	2026-01-21 14:47:13.568314	
86	162	Ulthera	4000.00	4000.00	f	\N	6	2026-01-21 14:47:13.568336	
87	167	Botox	1100.00	1100.00	t	2025-12-10 00:00:00	4	2026-01-21 18:04:37.272823	
88	167	Outros	1000.00	1000.00	f	\N	6	2026-01-21 18:04:37.272852	LIMELGIHTA PARA ROSACEA
89	169	Botox	1200.00	1200.00	t	2026-01-21 00:00:00	6	2026-01-21 18:30:00.503872	
90	169	Pearl Fracionado	1000.00	1000.00	f	\N	6	2026-01-21 18:30:00.503899	VALOR DE 1 SESSAO PARA ESTRIAS FAZER NO MINIMO 3 PAGA POR SESSAO
91	169	Morpheus	6000.00	6000.00	f	\N	6	2026-01-21 18:30:00.503906	FACE
92	173	Botox	1100.00	1100.00	t	2025-12-15 00:00:00	5	2026-01-21 20:16:32.69832	
93	177	Botox	1200.00	1200.00	t	2025-12-21 00:00:00	5	2026-01-21 20:23:13.956336	
94	177	Morpheus	6000.00	6000.00	f	\N	6	2026-01-21 20:23:13.956375	
95	179	Botox	1100.00	1100.00	t	2025-12-16 00:00:00	6	2026-01-21 20:24:43.207764	
96	179	Ulthera	4000.00	4000.00	f	\N	6	2026-01-21 20:24:43.207787	
97	185	Peeling	1300.00	1300.00	f	\N	6	2026-01-22 13:42:00.159118	peeling de ar para melasma
98	189	Botox	1200.00	1200.00	t	2025-12-10 00:00:00	6	2026-01-22 14:22:46.93398	
99	191	Botox	1200.00	1200.00	t	2025-12-16 00:00:00	5	2026-01-23 19:21:02.727465	dysport
100	195	Botox	1100.00	1100.00	t	2026-01-23 00:00:00	6	2026-01-23 20:04:22.960917	
101	195	Morpheus	18000.00	18000.00	f	\N	6	2026-01-23 20:04:22.960941	face e pescoco
102	200	Botox	1200.00	1200.00	t	2026-01-26 00:00:00	6	2026-01-26 18:18:55.825197	DYSPORT
103	200	Outros	2000.00	2000.00	t	2026-01-26 00:00:00	35	2026-01-26 18:18:55.825235	PEQUENA CIRURGIA
104	204	Botox	1800.00	1800.00	t	2026-01-26 00:00:00	6	2026-01-26 19:51:07.622331	com neferiti
105	204	Sculptra	2500.00	2500.00	f	\N	6	2026-01-26 19:51:07.622354	
106	206	Botox	1200.00	1200.00	f	\N	6	2026-01-26 20:12:56.688537	
107	210	Botox	1100.00	1100.00	t	2025-12-17 00:00:00	6	2026-01-27 14:28:35.081909	
111	224	Botox	1200.00	1200.00	f	\N	6	2026-01-27 14:34:29.541727	
112	224	Ulthera	2000.00	2000.00	f	\N	6	2026-01-27 14:34:29.541744	palpberas
114	233	Botox	1200.00	1200.00	t	2026-01-27 00:00:00	6	2026-01-27 18:35:09.139792	
115	239	Botox	1400.00	1400.00	t	2026-02-02 00:00:00	6	2026-02-02 14:04:05.243726	
116	245	Botox	1500.00	1500.00	t	2026-02-02 00:00:00	6	2026-02-02 15:13:14.608372	com nefertiit
117	245	Ulthera	4000.00	4000.00	t	2025-10-07 00:00:00	6	2026-02-02 15:13:14.608397	
120	252	Emtone	3200.00	3200.00	f	\N	6	2026-02-02 19:57:33.002371	
121	252	Preenchimento	1400.00	1400.00	f	\N	6	2026-02-02 19:57:33.002388	labial
122	258	Botox	1400.00	1400.00	t	2026-02-03 00:00:00	6	2026-02-03 13:40:43.335293	
123	258	Pearl Fracionado	4000.00	4000.00	f	\N	6	2026-02-03 13:40:43.335308	COM SEDACAO PARA CICATRIZ DE ACNE
124	258	Morpheus	6000.00	6000.00	f	\N	6	2026-02-03 13:40:43.335314	PARA CICATRIZ DE ACNE
125	264	Pearl Fracionado	1000.00	1000.00	t	2026-02-03 00:00:00	1	2026-02-03 17:28:00.032638	maos
126	268	Botox	1400.00	1400.00	t	2026-02-03 00:00:00	6	2026-02-03 20:04:17.324951	
127	268	Pearl Fracionado	4000.00	4000.00	f	\N	6	2026-02-03 20:04:17.324969	COM SEDACAO
128	274	Botox	14000.00	14000.00	t	2026-02-04 00:00:00	6	2026-02-04 17:32:21.603147	
129	277	Botox	1100.00	1100.00	f	\N	6	2026-02-04 19:08:39.009995	
130	280	Botox	1400.00	1400.00	f	\N	6	2026-02-05 13:03:12.436012	
131	280	Ulthera	6000.00	6000.00	f	\N	6	2026-02-05 13:03:12.436033	FACE E PESCOCO
132	282	Botox	1200.00	1200.00	t	2026-02-05 00:00:00	6	2026-02-05 14:36:32.545946	
133	282	Morpheus	6000.00	6000.00	f	\N	6	2026-02-05 14:36:32.545961	
134	282	Outros	2000.00	2000.00	f	\N	6	2026-02-05 14:36:32.545967	EXOSSOMOS PDRN
135	282	Preenchimento	1400.00	1400.00	f	\N	6	2026-02-05 14:36:32.545973	LABIOS
136	286	Botox	1200.00	1200.00	t	2026-02-05 00:00:00	6	2026-02-05 18:01:03.372332	
137	293	Botox	1200.00	1200.00	t	2026-01-28 00:00:00	6	2026-02-05 19:34:58.175419	
138	293	Sculptra	2500.00	2500.00	t	2026-02-05 00:00:00	6	2026-02-05 19:34:58.175437	
139	300	Botox	1200.00	1200.00	t	2026-02-11 00:00:00	6	2026-02-11 13:57:29.765202	
140	300	Preenchimento	1400.00	1400.00	f	\N	6	2026-02-11 13:57:29.765222	olheira
141	300	Preenchimento	1400.00	1400.00	f	\N	6	2026-02-11 13:57:29.765231	labios
142	300	Ulthera	3000.00	3000.00	f	\N	6	2026-02-11 13:57:29.765238	face e olhos
143	300	Peeling	600.00	600.00	f	\N	6	2026-02-11 13:57:29.765244	
144	307	Pearl Fracionado	500.00	500.00	t	2026-02-11 00:00:00	6	2026-02-11 17:49:47.007764	PERI-ORAL
145	309	Pearl Fracionado	2500.00	2500.00	f	\N	6	2026-02-11 18:11:35.343662	COM SEDAÇAO
146	309	Sculptra	5000.00	5000.00	f	\N	6	2026-02-11 18:11:35.34368	2 AMPOLAS FACE
147	309	Botox	1800.00	1800.00	f	\N	6	2026-02-11 18:11:35.343687	COM NEFERTITI
148	311	Botox	1400.00	1400.00	t	2026-02-11 00:00:00	6	2026-02-11 18:58:21.621047	
149	316	Outros	2500.00	2500.00	f	\N	6	2026-02-12 12:36:56.35975	pequena cirurgia para recuperar cicatriz  no nariz
150	322	Botox	1200.00	1200.00	t	2026-02-12 00:00:00	6	2026-02-12 18:37:21.533376	
151	324	Preenchimento	1400.00	1400.00	t	2026-02-13 00:00:00	6	2026-02-13 13:29:30.618532	labios
152	324	Sculptra	2500.00	2500.00	f	\N	6	2026-02-13 13:29:30.618569	1 ampola
153	324	Ulthera	2000.00	2000.00	f	\N	6	2026-02-13 13:29:30.618584	
154	330	Botox	1400.00	1400.00	t	2026-02-13 00:00:00	6	2026-02-13 18:40:32.199887	
155	330	Outros	7000.00	7000.00	f	\N	6	2026-02-13 18:40:32.199924	dermabrasao nariz com sedacao
156	341	Botox	1200.00	1200.00	t	2026-02-19 00:00:00	6	2026-02-19 20:30:43.29443	
157	341	Sculptra	5000.00	5000.00	f	\N	6	2026-02-19 20:30:43.294457	2 ampolas
158	346	Botox	1400.00	1400.00	t	2026-02-20 00:00:00	6	2026-02-20 18:55:42.912434	
159	348	Botox	1400.00	1400.00	t	2026-02-20 00:00:00	6	2026-02-20 18:57:25.904285	
160	350	Botox	1100.00	1100.00	t	\N	4	2026-02-20 18:59:27.310164	
161	350	Outros	1000.00	1000.00	f	\N	6	2026-02-20 18:59:27.310192	
162	350	Preenchimento	1400.00	1400.00	t	2026-02-20 00:00:00	6	2026-02-20 18:59:27.3102	
163	352	Botox	1200.00	1200.00	t	2026-02-20 00:00:00	6	2026-02-20 19:28:15.79923	
164	354	Botox	1400.00	1400.00	t	2026-02-25 00:00:00	6	2026-02-25 12:57:29.059874	
165	354	Peeling	1000.00	1000.00	f	\N	6	2026-02-25 12:57:29.0599	peeelgin facial por sessao malar
166	354	PEQUENA CIRURGIA	1000.00	1000.00	f	\N	6	2026-02-25 12:57:29.059907	cauterizacao glandula sebacea 
167	356	Emtone	3200.00	3200.00	f	\N	6	2026-02-25 14:06:01.134703	
168	356	Sculptra	6000.00	6000.00	f	\N	6	2026-02-25 14:06:01.134727	GLUTEOS ELLEVA X
169	366	Botox	1400.00	1400.00	t	2026-01-27 00:00:00	6	2026-02-27 18:31:45.089745	
170	370	LIMELIGHT FACE	1000.00	1000.00	t	2026-02-27 00:00:00	24	2026-02-27 18:43:09.315918	
171	370	Morpheus	6000.00	6000.00	t	2026-02-27 00:00:00	12	2026-02-27 18:43:09.315943	
172	372	Botox	1200.00	1200.00	t	2026-01-29 00:00:00	6	2026-02-27 19:36:04.340804	
173	372	Preenchimento	1800.00	1800.00	t	2026-02-27 00:00:00	6	2026-02-27 19:36:04.340827	volite peri oral
174	376	Botox	1400.00	1400.00	t	2026-01-27 00:00:00	6	2026-02-27 19:57:05.877284	
175	378	Botox	1400.00	1400.00	t	2026-02-27 00:00:00	6	2026-02-27 19:57:37.056068	
176	390	Botox	1200.00	1200.00	f	\N	6	2026-02-28 19:56:17.700707	
177	392	Botox	1200.00	1200.00	t	2026-02-27 00:00:00	6	2026-02-28 21:12:31.530411	
178	392	Botox	1000.00	1000.00	t	2026-02-27 00:00:00	6	2026-02-28 21:12:31.530428	Nefertiti
179	392	Botox	1000.00	1000.00	t	2026-02-27 00:00:00	6	2026-02-28 21:12:31.530433	Masseter
180	399	Botox	1400.00	1400.00	t	2026-02-02 00:00:00	5	2026-03-02 13:17:43.3096	
181	405	Botox	2000.00	2000.00	t	2026-03-02 00:00:00	6	2026-03-02 14:05:47.614308	face e nefertiti
182	405	Morpheus	18000.00	18000.00	t	2026-01-21 00:00:00	6	2026-03-02 14:05:47.614336	face e pesocoço
183	407	Botox	1100.00	1100.00	t	2026-03-02 00:00:00	6	2026-03-02 17:51:11.153988	
184	407	Preenchimento	1200.00	1200.00	t	2026-03-02 00:00:00	6	2026-03-02 17:51:11.154015	labios
185	409	Botox	1100.00	1100.00	t	\N	6	2026-03-02 18:04:42.888448	
186	409	Preenchimento	1200.00	1200.00	t	\N	6	2026-03-02 18:04:42.888476	
187	412	Botox	1800.00	1800.00	t	2026-01-26 00:00:00	6	2026-03-02 19:19:49.725929	neferititi
188	412	Sculptra	2500.00	2500.00	t	2026-02-05 00:00:00	6	2026-03-02 19:19:49.725951	
189	414	Botox	1200.00	1200.00	t	2026-02-02 00:00:00	6	2026-03-02 19:21:15.527168	
190	416	Botox	1200.00	1200.00	t	2026-02-02 00:00:00	6	2026-03-02 19:27:59.159517	
191	416	Ulthera	4000.00	4000.00	f	\N	6	2026-03-02 19:27:59.159541	
192	422	Botox	1200.00	1200.00	t	2026-03-02 00:00:00	6	2026-03-02 20:40:21.06816	
193	425	Ulthera	4000.00	4000.00	f	\N	6	2026-03-03 12:52:06.087627	
194	425	Botox	1200.00	1200.00	f	\N	6	2026-03-03 12:52:06.087651	
195	430	Preenchimento	1800.00	1800.00	f	\N	6	2026-03-03 13:47:58.554408	queixo pensei em 3 ampolas
196	430	Emsculpt Neo	3200.00	3200.00	f	\N	6	2026-03-03 13:47:58.554442	gluteo
197	430	Preenchimento	20000.00	20000.00	f	\N	6	2026-03-03 13:47:58.55445	gluteo 20 ml de cada lado por sessao
198	432	Botox	1200.00	1200.00	f	\N	6	2026-03-03 14:04:21.148276	
199	432	Preenchimento	20000.00	20000.00	f	\N	6	2026-03-03 14:04:21.1483	gluteo 40ml por sessao
200	432	Emsculpt Neo	3200.00	3200.00	f	\N	6	2026-03-03 14:04:21.148308	
201	440	PROTOCOLO MÃOS(LIMELIGHT + PEARL)	1000.00	1000.00	t	2026-02-23 00:00:00	6	2026-03-03 18:38:37.472006	
202	440	PEQUENA CIRURGIA	1800.00	1800.00	f	2026-02-23 00:00:00	6	2026-03-03 18:38:37.472025	cauterizacao e exerese de lesao
203	440	Botox	1200.00	1200.00	f	\N	6	2026-03-03 18:38:37.472032	
204	440	Peeling	600.00	600.00	f	\N	6	2026-03-03 18:38:37.472038	1 sessao
205	447	Botox	1200.00	1200.00	t	2026-03-03 00:00:00	6	2026-03-03 20:31:55.697392	
206	447	MD Codes	5000.00	5000.00	f	\N	6	2026-03-03 20:31:55.697424	3 ampolas 
207	447	Sculptra	2500.00	2500.00	f	\N	6	2026-03-03 20:31:55.697432	
208	458	Botox	1200.00	1200.00	f	\N	6	2026-03-04 13:42:55.900387	
209	461	Botox	1200.00	1200.00	t	2026-03-04 00:00:00	6	2026-03-04 15:00:02.182745	
210	461	MD Codes	3000.00	3000.00	f	\N	6	2026-03-04 15:00:02.182769	2 AMPOLAS  Q CKQ E CK2 E SULCO INFEIROR
211	461	Peeling	600.00	600.00	f	\N	6	2026-03-04 15:00:02.182777	AR 5
212	461	Ulthera	4000.00	4000.00	f	\N	6	2026-03-04 15:00:02.182783	
213	463	Botox	1400.00	1400.00	t	2026-03-04 00:00:00	6	2026-03-04 15:05:52.475815	
214	466	Botox	1200.00	1200.00	t	2026-03-04 00:00:00	6	2026-03-04 18:00:50.509714	
215	472	Botox	1200.00	1200.00	t	2026-03-04 00:00:00	6	2026-03-04 19:33:51.751776	
216	472	Morpheus	6000.00	6000.00	f	\N	6	2026-03-04 19:33:51.751802	
217	472	PDRN	1000.00	1000.00	f	\N	6	2026-03-04 19:33:51.75181	
218	476	Botox	1200.00	1200.00	t	2026-03-04 00:00:00	6	2026-03-04 19:58:32.679557	
219	494	Botox	1400.00	1400.00	t	2026-03-05 00:00:00	5	2026-03-05 20:49:11.321454	
220	499	Botox	1200.00	1200.00	f	\N	6	2026-03-06 14:24:35.829312	
221	502	Sculptra	6000.00	6000.00	t	2026-03-09 00:00:00	6	2026-03-09 13:14:16.146376	GLUTEOS ELLEVA X
222	502	Outros	4000.00	4000.00	f	\N	6	2026-03-09 13:14:16.146398	SUBCISAO COM ELLEVA X NO CC
223	517	Ulthera	4000.00	4000.00	f	\N	6	2026-03-09 20:25:43.140677	foco na papada
224	517	Botox	1200.00	1200.00	f	\N	6	2026-03-09 20:25:43.140693	
225	519	Morpheus	18000.00	18000.00	f	\N	6	2026-03-10 11:38:54.775668	face pescoco e colo
226	519	Morpheus	32000.00	32000.00	f	\N	6	2026-03-10 11:38:54.775685	morpheus full body 32000
227	519	Sculptra	6000.00	6000.00	f	\N	6	2026-03-10 11:38:54.775689	elleva x abdome e banananinha
228	521	Botox	1100.00	1100.00	t	2026-03-10 00:00:00	6	2026-03-10 13:07:18.402228	
229	521	Ulthera	4000.00	4000.00	f	\N	6	2026-03-10 13:07:18.402252	
230	527	Botox	1100.00	1100.00	t	2026-03-10 00:00:00	6	2026-03-10 18:40:59.905798	
231	527	Morpheus	6000.00	6000.00	f	\N	6	2026-03-10 18:40:59.905819	face
232	529	Botox	1100.00	1100.00	t	2026-03-10 00:00:00	6	2026-03-10 18:52:43.194922	
233	529	Botox	1100.00	1100.00	f	\N	6	2026-03-10 18:52:43.194948	masster
234	529	Ulthera	4000.00	4000.00	f	\N	6	2026-03-10 18:52:43.194956	face
235	537	Pearl Fracionado	2500.00	2500.00	t	2026-03-11 00:00:00	6	2026-03-11 13:01:39.345767	
236	537	Sculptra	5000.00	5000.00	t	2026-03-11 00:00:00	6	2026-03-11 13:01:39.3458	
237	537	Botox	1800.00	1800.00	f	\N	6	2026-03-11 13:01:39.345808	
238	537	Ulthera	2000.00	2000.00	t	2026-03-11 00:00:00	6	2026-03-11 13:01:39.345814	papada
239	545	Botox	1400.00	1400.00	t	2026-03-11 00:00:00	6	2026-03-11 15:26:06.307952	
240	557	Morpheus	20000.00	20000.00	t	2026-03-12 00:00:00	6	2026-03-12 12:22:11.460718	
241	557	Morpheus	32000.00	32000.00	f	\N	6	2026-03-12 12:22:11.460745	
242	557	Sculptra	6000.00	6000.00	f	\N	6	2026-03-12 12:22:11.460753	
243	562	Preenchimento	1400.00	1400.00	f	\N	6	2026-03-12 12:44:38.627207	sulco nasogeniano e algumas ruguinha peri oral
244	567	Botox	1100.00	1100.00	t	2026-03-12 00:00:00	6	2026-03-12 17:57:29.96731	
245	567	Preenchimento	2800.00	2800.00	t	2026-03-12 00:00:00	6	2026-03-12 17:57:29.967336	1 ampola ck1 ck2 e 1 ampola contonro queixo
246	567	Outros	400.00	400.00	t	2026-03-12 00:00:00	6	2026-03-12 17:57:29.967343	infiltracao capilar /sessao
247	569	Botox	1200.00	1200.00	f	\N	6	2026-03-12 17:59:08.778264	
248	569	Preenchimento	2800.00	2800.00	f	\N	6	2026-03-12 17:59:08.778304	contorno 2 ampolas
249	569	Sculptra	5000.00	5000.00	t	2026-03-12 00:00:00	6	2026-03-12 17:59:08.778312	
250	569	Pearl Fracionado	2500.00	2500.00	f	\N	6	2026-03-12 17:59:08.778319	face completa
251	572	Outros	2500.00	2500.00	t	2026-03-12 00:00:00	6	2026-03-12 18:36:27.829023	ferrinjet e soroterapia 1 sessao
252	577	LIMELIGHT FACE	1000.00	1000.00	t	2026-03-12 00:00:00	6	2026-03-12 19:19:11.132038	a segunda sessao face 20
253	577	Ulthera	4000.00	4000.00	f	\N	6	2026-03-12 19:19:11.132063	
254	577	Peeling	400.00	400.00	f	\N	6	2026-03-12 19:19:11.132071	
255	577	Botox	1200.00	1200.00	f	\N	6	2026-03-12 19:19:11.13208	
256	579	Botox	1800.00	1800.00	f	\N	6	2026-03-12 19:59:03.535344	com neferiti
257	579	Morpheus	12000.00	12000.00	f	\N	6	2026-03-12 19:59:03.535376	face e pescoco
258	581	Botox	1800.00	1800.00	f	\N	6	2026-03-12 19:59:14.855717	com neferiti
259	581	Morpheus	12000.00	12000.00	f	\N	6	2026-03-12 19:59:14.855744	face e pescoco
260	583	Preenchimento	1400.00	1400.00	f	\N	6	2026-03-12 20:16:59.800138	
261	583	Preenchimento	1400.00	1400.00	f	\N	6	2026-03-12 20:16:59.800161	sulco e rugas finas perioral
\.


--
-- Data for Name: doctor_preference; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.doctor_preference (id, user_id, color, layer_enabled, created_at) FROM stdin;
\.


--
-- Data for Name: encounter_cp; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.encounter_cp (id, doctor_id, doctor_patient_id, created_at, updated_at, category, complaint_text, plan_summary_text, consultation_seconds, status) FROM stdin;
1	7	343	2026-03-04 11:54:55.300188	2026-03-04 12:13:35.47813	FACE			89	DRAFT
2	7	362	2026-03-04 19:26:58.407347	2026-03-04 19:28:04.325152	CORPORAL	facelift deep plane mais palpebras		69	DRAFT
\.


--
-- Data for Name: evolution; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.evolution (id, patient_id, doctor_id, evolution_date, content, created_at, consultation_id) FROM stdin;
13	11	5	2025-12-02 02:32:00	???	2025-12-02 02:32:46.878956	\N
14	11	5	2025-12-02 02:48:00	Teste	2025-12-02 02:49:03.972484	\N
15	11	5	2025-12-02 02:58:00	Teste 2	2025-12-02 02:58:07.58199	\N
16	11	5	2025-12-02 03:17:00	Teste 3	2025-12-02 03:18:13.446549	\N
17	11	5	2025-12-02 03:17:00	Teste 3	2025-12-02 03:18:13.72597	\N
18	11	5	2025-12-02 03:23:00	Teste 4	2025-12-02 03:23:52.024789	\N
19	11	5	2025-12-02 03:26:00	Teste 5	2025-12-02 03:26:43.379526	\N
20	30	5	2025-07-10 20:07:00	1 semana pos op sem crostas	2025-12-03 20:07:59.81279	39
21	54	5	2026-01-19 17:37:00	tem uma papaulas na face falei de fazer 3 para testar se vai manchar	2026-01-19 17:38:07.871711	69
23	63	5	2026-01-19 19:40:00	fez hoje ulthera	2026-01-19 19:40:22.867149	78
24	70	5	2026-01-21 15:32:00	retoque botox	2026-01-21 15:32:16.505277	85
25	97	5	2026-01-22 14:24:00	retoque botox	2026-01-22 14:24:38.098604	142
30	103	5	2026-02-20 15:58:00	FEC HJ PREENCHIMENTO DE OLEHRAS USEI 0,8ML RESTYLANE	2026-02-20 18:58:32.606156	126
31	62	5	2026-02-26 09:23:00	retoque botox 25u	2026-02-26 12:23:13.591183	77
1	1	5	2025-11-28 19:52:00	eritema pos morphues	2025-11-28 19:52:45.995347	13
26	135	5	2026-02-19 15:11:00	evoluiu bem com 20 dias de bactrin porem ainda tem inflamcao leve falço 10 dias de pred 3 2 e 1cp por dia c	2026-02-19 18:11:39.287467	284
32	49	5	2025-12-09 13:15:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:19.719881	64
33	48	5	2025-12-09 13:30:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: fez 2 aplicaoes de infltracao capilar fechou pacote com 4 \n\nhj ja esta cheio de cabelinhos	2026-02-28 02:01:19.854353	62
34	50	5	2025-12-10 14:30:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:20.066694	65
35	35	5	2025-12-04 15:00:00	Queixa principal: estrias nas pernas\n verrugas curadas\n\nExame/Anamnese: estrias vermelhas interno de coxa e coxa\n\nConduta: striactive e vitanl 0,5	2026-02-28 02:01:20.364312	46
36	58	5	2025-12-11 09:00:00	Queixa principal: lipedema\n\nExame/Anamnese: edema e espessamento dos mmmii\n\nDiagnóstico: lipedema\n\nConduta: orientacoa exercicio fisico	2026-02-28 02:01:20.491098	73
37	18	5	2025-12-02 08:00:00	Queixa principal: manchas na pele\n\nExame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\n\nmelanose solar e lentigo solar na face\ndermatofibroma no joelho\n\nDiagnóstico: lentigo solar \ndermatofibroma\n\nConduta: Uso Tópico\ncetaphil percting serum anti manchas\nAPLICAR NO ROSTO à NOITE E RETIRAR PELA MANHÃ\nHYDROBOOST GEL DE LIMPEZA NEUTROGENA\nLAVAR O ROSTO 2X/DIA POR DIA\nEpisol Color FPS 70\nAPLICAR NO ROSTO 1-2X/DIA	2026-02-28 02:01:20.87081	25
38	170	5	2026-02-03 16:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:21.082114	199
39	60	5	2025-12-11 17:00:00	Queixa principal: MELASMA\n\nExame/Anamnese: HIPERCERATOSE FOLICULAR GLUTEO\nMELASMA\n\nConduta: herapsor solucao\naplicar 8 -10 gotas na regiao afetada 1 x/dia por 5 dias reutilizar se necessa´rio\nEPIDRAT CALM\nAPLICAR NO ROSTO 3-4X/DIA\nAnti-Pigment Dual Sérum\naplicar no rosto À noite e retirar pela manhã\ncleanance gel\nLAVAR O ROSTO 2X/DIA\nAnti-Pigment Creme Corporal para Áreas Específicas\nAplicar uma fina camada nas áreas com manchas 1-2 vezes ao dia	2026-02-28 02:01:21.293336	75
40	19	5	2025-12-02 09:00:00	Queixa principal: quer fazer btoox\n\nExame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:21.546674	26
41	65	5	2025-12-11 15:15:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:21.758947	80
42	81	5	2025-12-12 16:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:21.886012	97
43	75	5	2025-12-12 07:30:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nConduta: O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	2026-02-28 02:01:22.097207	90
44	66	5	2025-12-12 09:00:00	Exame/Anamnese: prurigo no corpo todo e rosacea\n\ntrattou com limecilina 12/12 sem melhora da rosacea\nacho q tem aver com o barbear\n\nConduta: Uso Tópico\nSUNFRESH OIL CONTROL FPS80 NEUTROGENA\nAPLICAR NO ROSTO 2X/DIA\nsuavie sabonete liquido\nlavar o rosto 2x/dia\nEPIDRAT CALM\nAPLICAR NO ROSTO 3-4X/DIA\n\n\ndoxaciclina 100mg\n\nTomar 1cp vo de 12/12h por 30 dias\n\nUso Tópico\n\n1.\nrozex\n\nAplicar no rosto à noite e retirar pela manhã	2026-02-28 02:01:22.226318	81
45	72	5	2025-12-12 14:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:22.43764	87
46	94	5	2025-12-16 09:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:22.649114	112
47	84	5	2025-12-15 13:00:00	Queixa principal: mancha na pele\n\nExame/Anamnese: 2 nevos na regiao da costeleta\n\nDiagnóstico: lentigo solar e qs\n\nConduta: orientacao	2026-02-28 02:01:22.77578	101
48	2	5	2025-11-25 15:30:00	Queixa principal: rugas na face\n\nExame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:23.244221	2
49	20	5	2025-12-02 10:00:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nExame/Anamnese: area doadora muito ruim\n barba e peito bom\n\nConduta: O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	2026-02-28 02:01:23.792783	27
50	21	5	2025-12-02 12:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: advatan\naplicar nas lesoes 1x/dia por 5 dias\nCreme Facial Diário Fisiogel A.I.\nAPLICAR NO ROSTO 2-3X/DIA\nEPIDRAT CALM\nAPLICAR NO ROSTO 3-4X/DIA	2026-02-28 02:01:24.264324	28
51	25	5	2025-12-02 13:30:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: na verdade hj fez retoque botox	2026-02-28 02:01:24.518095	32
52	17	5	2025-11-28 16:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:24.816523	22
53	82	5	2025-12-15 09:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:25.027838	99
54	89	5	2025-12-15 14:30:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nConduta: O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	2026-02-28 02:01:25.155458	107
55	86	5	2025-12-15 10:30:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:25.281871	103
56	92	5	2025-12-15 16:30:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:25.409467	110
57	99	5	2026-01-19 15:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:25.536998	121
58	48	5	2025-12-17 08:30:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:25.664602	115
59	98	5	2026-01-19 17:30:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:25.960558	119
60	107	5	2026-01-21 15:30:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nConduta: O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	2026-02-28 02:01:26.130043	132
61	96	5	2026-01-21 15:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:26.426991	130
62	105	5	2026-01-21 14:30:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: Paciente: LUCIANA FINOTO MELO\n\nUso Tópico\nderivamicro\nAPLICAR NO ROSTO à NOITE E RETIRAR PELA MANHÃ\nHyalu B5 Serum\nAPLICAR NO ROSTO à NOITE E RETIRAR PELA MANHÃ\nefaclar alta tolerancia\nlavar o rosto 2x/dia\nessencele c 20\nAPLICAR NO ROSTO PELA MANHA ANTES DO FPS	2026-02-28 02:01:26.554251	129
63	115	5	2026-01-22 10:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nDiagnóstico: acne da mulher adulta\n\nConduta: ja usou limeciclina 4 meses e zella\ncom otimo resultado\npara acne indico pacte peeling para melasma\ne introduzo vitacidplus tambem	2026-02-28 02:01:26.680951	140
64	113	5	2026-01-22 09:00:00	Conduta: retinol b3 serum\ncerave olhos\n\nindico cirurgiao plasstico para tirar nevos pq marido é medico da unimed	2026-02-28 02:01:26.807969	138
65	116	5	2026-01-22 10:30:00	Queixa principal: quedad de cabelo pos face\ndermatofibroma na coxa\nnevo rubi no seio\n\nConduta: NOURKRIN\nTOMAR 1 CP VO PELA MANHÃ E 1 CP VO à NOITE POR 3 MESES\ncollagen h.a mantecorp\ntomar 1 sachet por dia por 3 meses\nUso Tópico\nRetinol B3 Serum\nAPLICAR NO ROSTO à NOITE E RETIRAR PELA MANHÃ\nessencele c 20\nAPLICAR NO ROSTO PELA MANHA ANTES DO FPS\nk-ox eye\naplicar nas areas dos olhos 2x/dia\n\nvitacidplus e eucerin corpoarl para mancha pos subcisao no gluteo	2026-02-28 02:01:26.935337	141
66	11	5	2025-11-27 17:00:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nExame/Anamnese: perda do recesso frontal mantem topete e coroa\n\nDiagnóstico: calvice grau 4\n\nConduta: O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	2026-02-28 02:01:27.316073	23
67	33	5	2025-12-03 14:00:00	Queixa principal: nodulo na face\n\nExame/Anamnese: ultrassom  fala a favor de granuloma\n\nnao indetifica se é biosestimulador ou acido hialuronico\n\nnodulo na regiao malar visivel e palpavel\n\nDiagnóstico: granuloma\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:28.036358	44
68	28	5	2025-12-03 09:15:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nConduta: transplnate coroa	2026-02-28 02:01:28.206584	36
69	34	5	2025-12-04 11:30:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:28.333271	45
70	47	5	2025-12-09 14:00:00	Queixa principal: ja faz botox\n\nExame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:28.460346	61
71	46	5	2025-12-09 14:30:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:28.587311	60
72	80	5	2025-12-15 11:00:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nConduta: O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	2026-02-28 02:01:28.714603	104
73	42	5	2025-12-09 16:30:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nConduta: O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	2026-02-28 02:01:28.841803	56
74	67	5	2025-12-12 09:15:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:28.968994	82
75	44	5	2025-12-09 15:30:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nConduta: O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	2026-02-28 02:01:29.180503	58
76	43	5	2025-12-09 16:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:29.307052	57
77	41	5	2025-12-09 17:00:00	Exame/Anamnese: sulco papada\npalpebras\n\nDiagnóstico: estetica\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:29.434199	55
78	51	5	2025-12-10 14:45:00	Exame/Anamnese: afinamento do cabelo em uso de megahair\ntem baby hair na hairline\n\nConduta: NEOSIL ATTACK\nTOMAR 1 CP VO POR DIA POR 3 MESES\nMINOXIDIL 1MG (USO CONTINUO)\nTOMAR 1 CP VO POR DIA	2026-02-28 02:01:29.646297	66
79	52	5	2025-12-10 15:00:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nConduta: O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	2026-02-28 02:01:29.773443	67
80	57	5	2025-12-10 15:30:00	Queixa principal: alvicie feminina\nrarefacao homogenea\n.\n\nExame/Anamnese: area doadora muito ruim fio muito fino\n\nDiagnóstico: alopecia androgenetica feminina\n\nConduta: fazer o transpalnte na menor area possivel\n areadoadora ruim\nmuito fino ralo pensei 2000-2500	2026-02-28 02:01:29.901294	72
81	104	5	2026-01-21 11:30:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:30.070434	128
82	59	5	2025-12-11 09:30:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: botox 30u	2026-02-28 02:01:30.197594	74
83	37	5	2025-12-05 09:15:00	Queixa principal: fez botox ha 1 mes\n\nExame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: reveline retinol\nefaclar concetrado\nfps	2026-02-28 02:01:30.324602	50
84	36	5	2025-12-05 17:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:30.451305	49
85	39	5	2025-12-05 17:30:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nConduta: O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	2026-02-28 02:01:30.578614	52
86	38	5	2025-12-05 14:00:00	Queixa principal: ja fez um trnasplante ha 1 ano\n\nConduta: O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	2026-02-28 02:01:30.705977	51
87	95	5	2025-12-16 09:30:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:31.170777	113
88	61	5	2025-12-11 10:45:00	Exame/Anamnese: CALVICIE FEMININA JA FEZ TRANSPLANTE CAPILAR EM OUTRO SERVICO\n\nDiagnóstico: ALOPECIA ANDROGENETICA FEMINA\n\nConduta: FEZ HJ INFILTRACAO CAPILAR	2026-02-28 02:01:31.298481	76
89	64	5	2025-12-11 14:30:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:31.46758	79
90	77	5	2025-12-12 15:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:31.765149	92
91	78	5	2025-12-12 15:30:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:31.892317	96
92	74	5	2025-12-12 17:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: etirp no queixo deixo corticoide caso precise	2026-02-28 02:01:32.019809	89
93	1	5	2025-12-12 11:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:32.278604	98
94	83	5	2025-12-15 09:30:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:32.489718	100
95	85	5	2025-12-15 10:00:00	Queixa principal: dermatofibroma\n\nExame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:32.702253	102
96	54	5	2026-01-19 15:30:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:32.829512	120
97	100	5	2026-01-19 16:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: melanose solar e lentigo solar quer tirar\n\ntalvez limeght\n\npasso dual serum e fusion water	2026-02-28 02:01:32.957596	122
98	63	5	2026-01-19 14:15:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:33.08456	118
99	108	5	2026-01-21 16:00:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nConduta: O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	2026-02-28 02:01:33.211724	133
100	109	5	2026-01-21 16:30:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:33.338882	134
101	111	5	2026-01-21 17:15:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:33.465397	136
102	101	5	2026-01-21 09:30:00	Conduta: sunfresh e orientação geral	2026-02-28 02:01:33.676854	124
103	102	5	2026-01-21 10:30:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nConduta: O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	2026-02-28 02:01:33.803991	125
104	114	5	2026-01-22 09:15:00	Diagnóstico: queimadura solar na face\n\nConduta: nevo ok\n apenas orientacao	2026-02-28 02:01:34.057353	139
105	121	5	2026-01-23 16:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:34.184674	147
106	120	5	2026-01-23 15:30:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nConduta: O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	2026-02-28 02:01:34.311297	146
107	123	5	2026-01-23 16:30:00	Queixa principal: espihjas ja usou epiduo agora troquei por clindoxyul\n\nConduta: melhora parcial em um de progesterona como aco\n\ninicio espiro 200\nhyalu b5 water gel	2026-02-28 02:01:34.43816	149
108	122	5	2026-01-23 15:45:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:34.56577	148
109	74	5	2026-01-27 09:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:34.945071	157
110	124	5	2026-01-26 11:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nDiagnóstico: NEVO MELANOCITICO\n\nConduta: FAÇO HJ EXERESE DE LESAO NA FACE NEVO MELANOCITICO	2026-02-28 02:01:35.072478	150
111	128	5	2026-01-26 16:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:35.368237	154
112	131	5	2026-01-27 09:30:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nConduta: O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\nFAZER 70 COROA E 30 FRONTAL SO ENTRADINHA  OU 60 40	2026-02-28 02:01:35.495078	158
113	133	5	2026-01-27 10:30:00	Queixa principal: paciente veio ha 1 mes com foliclute ecorida nas costas tipo um eczema folicular\ntratei com diporspan e halobex e atoderm com melhora completa poem hj teve uma erupcao acneiforme nas costas e voltou um pouco as lesoes  mas bem mais brandas q da outra vez\n\nConduta: melhora parcial\n foi totalnos primeiros dias mas ainda tem lesoe sbem foliculares\ninicio limecilina ate pq alem de ser um foliculitre teve uma erupcao acneiforme	2026-02-28 02:01:35.706459	160
114	136	5	2026-01-27 11:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:35.834012	163
115	173	5	2026-02-04 10:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:35.961002	202
116	175	5	2026-02-04 11:00:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nExame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	2026-02-28 02:01:36.087467	204
117	181	5	2026-02-05 14:30:00	Queixa principal: ACNE\n\nDiagnóstico: ACNE LEVE\n\nConduta: USO DE EPIDUO	2026-02-28 02:01:36.304673	210
118	179	5	2026-02-05 10:00:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nConduta: FINASTEIRDA 5MG JA TOMA MINOXIDIL ORAL\nORIENTACAO GERAL	2026-02-28 02:01:36.432879	208
119	228	5	2026-02-12 09:30:00	Queixa principal: tem uma cicatr larga no nariz\n\ne cicatriz de acne\n\n\nindico cirurgia para cicatriz que é larga 2500\n\ne genesis  para cicatriz de acne\nUso Oral\nMINOXIDIL 1MG (USO CONTINUO)\nTOMAR 1 CP VO POR DIA\nUso Tópico\ncappy\nAPLICAR NO COURO CABELUDO 1X/DIA à NOITE\n\nExame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: tem uma cicatr larga no nariz\n\ne cicatriz de acne\n\n\nindico cirurgia para cicatriz que é larga 2500\n\ne genesis  para cicatriz de acne\nUso Oral\nMINOXIDIL 1MG (USO CONTINUO)\nTOMAR 1 CP VO POR DIA\nUso Tópico\ncappy\nAPLICAR NO COURO CABELUDO 1X/DIA à NOITE	2026-02-28 02:01:36.731404	260
120	216	5	2026-02-11 10:00:00	Queixa principal: NEVO CONGENITO NA ORELHA ESQUERDA\n\nConduta: DERMATOSCOPIA OK SEM ALETRACOES NEVO INVADE O CONDUTO	2026-02-28 02:01:37.036875	248
121	248	5	2026-02-19 11:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:37.418544	285
122	256	5	2026-02-20 11:00:00	Queixa principal: QUEDA DE CABELO\n\nConduta: 📋 RECEITA EMITIDA:\nQUEDA DE CABELO SEM SINAIS CLINICA EM USO DE TESTO NAO CONSEGUIU USAR A DUTASTERIDA\nNAOA CHO Q SEJA ACLVICIE SO QUEDA MESMO	2026-02-28 02:01:37.630448	294
123	268	5	2026-02-25 10:15:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:37.757896	308
124	296	5	2026-02-27 10:30:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nConduta: O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\ninicio finasterida	2026-02-28 02:01:38.307465	340
125	306	5	2026-02-27 17:15:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:38.434394	350
126	130	5	2026-01-26 17:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:38.56122	156
127	132	5	2026-01-27 10:00:00	Queixa principal: hiperceratose folicular nos bracos e pernas\n\nConduta: formula	2026-02-28 02:01:38.688319	159
128	172	5	2026-02-04 09:30:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nConduta: O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\nminoxidil 2,5	2026-02-28 02:01:38.815457	201
129	134	5	2026-01-27 10:30:00	Queixa principal: queda de cabelo\n\nConduta: Uso Oral\nNEOSIL ATTACK\nTOMAR 1 CP VO POR DIA POR 3 MESES\nUso Tópico\nAnti-Pigment Dual Sérum\naplicar no rosto À noite e retirar pela manhã\nessencele c 20\nAPLICAR NO ROSTO PELA MANHA ANTES DO FPS\nivy c corpo\naplicar no colo 1-2x/dia	2026-02-28 02:01:38.94242	161
130	135	5	2026-01-27 10:45:00	Queixa principal: furunculose ou paniculite pos enximas\n\nConduta: bactrin f 12/12 10 dias	2026-02-28 02:01:39.069546	162
131	140	5	2026-01-27 15:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:39.197273	167
132	141	5	2026-01-27 15:15:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nConduta: O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	2026-02-28 02:01:39.324374	168
133	254	5	2026-02-20 10:00:00	Queixa principal: QUEDA DE CA\n\nExame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:39.537421	292
134	103	5	2026-02-20 15:15:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:39.664564	302
135	223	5	2026-02-11 16:30:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nConduta: O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\niniciar trataqmento depois parou ha 2 anos	2026-02-28 02:01:39.792607	255
136	188	5	2026-02-05 16:45:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:39.920332	217
137	187	5	2026-02-05 16:30:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nConduta: O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n🧾 PRESCRIÇÃO MÉDICA\n\nPaciente: DIOGO ARROYO\n\n💊 Uso Oral:\n- NEOSIL ATTACK\n  TOMAR 01 CP VO POR DIA POR 3 MESES\n- MINOXIDIL 2,5MG\n  TOMAR 01 CP VO POR DIA\n- FINASTERIDA 1MG\n  TOMAR 1 CP VO POR DIA\n\n🧴 Uso Tópico:\n- CAPPY\n  APLICAR NO COURO CABELUDO 1X/DIA\n\nDr. Arthur Basile – CRM 125.217\nDermatologista\n\nClínica Basile – Av. Prof. João Fiúsa, 2300 – Ribeirão Preto – SP\nwww.clinicabasile.com.br | Fone/Fax: (16) 3602-7785	2026-02-28 02:01:40.047615	216
138	225	5	2026-02-11 10:15:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: zella\naplicar no rosto À noite e retirar pela manhã\nAnti-Pigment Dual Sérum\naplicar no rosto À noite e retirar pela manhã\nefaclar alta tolerancia\nlavar o rosto 2x/dia\nessencele c 20\nAPLICAR NO ROSTO PELA MANHA ANTES DO FPS	2026-02-28 02:01:40.343062	257
139	227	5	2026-02-12 09:00:00	Queixa principal: nao teve melhora da foliculite ainda se queixa muito]\n\nmas nitidamente nao tem foliculite tem apenas  prurigo\n\npasso hixiinze 30 dias e therapsor 10 dias\n\nDiagnóstico: prurigo no couro cabeludo e no peito\nnao tem foliculite\n\nConduta: nao teve melhora da foliculite ainda se queixa muito]\n\nmas nitidamente nao tem foliculite tem apenas  prurigo\n\npasso hixiinze 30 dias e therapsor 10 dias\n\nse nao melhorar pensei em limecilinas	2026-02-28 02:01:40.470732	259
140	261	5	2026-02-20 16:30:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:40.767532	299
141	232	5	2026-02-12 14:45:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:40.894489	265
142	239	5	2026-02-13 09:30:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:41.275357	272
143	238	5	2026-02-13 09:51:00	Queixa principal: granuloma no piercing\n\nConduta: diprogenta e fentizol	2026-02-28 02:01:41.572463	271
144	265	5	2026-02-25 09:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: 📋 RECEITA EMITIDA:	2026-02-28 02:01:41.784333	305
145	249	5	2026-02-19 15:00:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nConduta: O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n\n\n📋 RECEITA EMITIDA:	2026-02-28 02:01:42.080372	286
146	281	5	2026-02-26 10:00:00	Queixa principal: papulas foliculares\n\nConduta: boa melhora\ntinha acne no doroso pos diprospan\n hj praticamente sem anda\n mantive o antibiotico mais 15 dias 12/12\nacho q tem estrese evnolvido parou muito no carnaval\n\nse nao melhorar pensei em biopsia pra excluir liquen plano pilar	2026-02-28 02:01:42.968761	324
147	299	5	2026-02-27 14:45:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:43.179748	343
148	126	5	2026-01-26 15:00:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nConduta: O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	2026-02-28 02:01:43.306881	152
149	171	5	2026-02-04 09:00:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nConduta: O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n🧾 PRESCRIÇÃO MÉDICA\n\nPaciente: ALEXANDRE VINICIUS DA SILVA PEREIRA\n\n💊 Uso Oral:\n- NEOSIL ATTACK\n  TOMAR 01 CP VO POR DIA POR 3 MESES\n- MINOXIDIL 2,5MG\n  TOMAR 01 CP VO POR DIA\n\n🧴 Uso Tópico:\n- CAPPY\n  APLICAR NO COURO CABELUDO 1X/DIA\n\nDr. Arthur Basile – CRM 125.217\nDermatologista\n\nClínica Basile – Av. Prof. João Fiúsa, 2300 – Ribeirão Preto – SP\nwww.clinicabasile.com.br | Fone/Fax: (16) 3602-7785	2026-02-28 02:01:43.43411	200
150	137	5	2026-01-27 11:15:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	2026-02-28 02:01:43.561254	164
151	138	5	2026-01-27 11:30:00	Queixa principal: nevo com padrao globular no couro cabeludo com assimetria\n\nConduta: faço exerese hj	2026-02-28 02:01:43.688462	165
152	144	5	2026-01-27 16:30:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nConduta: O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\nininciar tratamento depois	2026-02-28 02:01:43.900417	171
153	177	5	2026-02-05 09:00:00	Queixa principal: NEVO NA FACE\n\nExame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:44.029096	206
154	182	5	2026-02-05 14:45:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:44.240372	211
155	226	5	2026-02-11 10:45:00	Queixa principal: PV ZILERI POSITIVO\n\nConduta: cetoconazol 200mg\ntomar 1 cp vo por dia por 15 dias\nUso Tópico\nicaden spray\naplicar no corpo 2x/dia por 15 dias\natoderm gel creme\nAPLICAR NO CORPO 3-4X/DIA	2026-02-28 02:01:44.452291	258
156	218	5	2026-02-11 11:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:44.579924	250
157	189	5	2026-02-06 09:00:00	Queixa principal: cisto sebaceo na face ha 3 meses\n\nDiagnóstico: cisto sebaceo\n\nConduta: oriento exerese da lesao\n1800 reais pcte tem unimed	2026-02-28 02:01:44.876455	218
158	219	5	2026-02-11 14:30:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:45.34054	251
159	271	5	2026-02-25 11:15:00	Queixa principal: calvicie  vem fazndo infiltracao capilar\n\nConduta: ifiltracao capilar	2026-02-28 02:01:46.482758	311
160	262	5	2026-02-13 15:30:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:46.864094	300
161	246	5	2026-02-19 09:30:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nConduta: O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	2026-02-28 02:01:46.992204	282
162	257	5	2026-02-20 14:30:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:47.458952	295
163	282	5	2026-02-26 10:30:00	Queixa principal: cicatriz hipertrofica no umbiogo\ndescamacao no couro cabeludo\ne melasma leve\n\nConduta: 📋 RECEITA EMITIDA: indico laser cicatriz ascne	2026-02-28 02:01:47.763026	325
164	305	5	2026-02-27 17:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:48.143501	349
165	286	5	2026-02-26 15:15:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nConduta: O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	2026-02-28 02:01:48.271293	329
166	106	5	2026-02-03 14:30:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nConduta: O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	2026-02-28 02:01:48.48346	191
167	149	5	2026-02-02 10:00:00	Conduta: nl\n verrugas no pe	2026-02-28 02:01:49.032384	176
168	147	5	2026-02-02 09:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:49.160064	174
169	217	5	2026-02-11 10:30:00	Conduta: NL	2026-02-28 02:01:49.287226	249
170	151	5	2026-02-02 11:00:00	Queixa principal: qa e ds\n\nDiagnóstico: qs \nqa\nds\n\nConduta: doctar\ntarfic\nsunfres oil conrtol	2026-02-28 02:01:49.498448	178
171	159	5	2026-02-02 12:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:49.626531	186
172	180	5	2026-02-05 10:30:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:49.752904	209
173	156	5	2026-02-02 16:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nDiagnóstico: qs na face\nfibroma mole no gluteo\ncelulite\nespodnilite anquilosante me uso de ce e imnubiologico\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:50.048658	183
174	160	5	2026-02-02 13:30:00	Queixa principal: verruga plantar\n\nConduta: nl	2026-02-28 02:01:50.259304	187
175	184	5	2026-02-05 15:30:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nConduta: O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	2026-02-28 02:01:50.894662	213
176	118	5	2026-02-03 09:00:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nConduta: O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\ntiro foto 03/2/26	2026-02-28 02:01:51.022621	188
177	161	5	2026-02-03 09:30:00	Diagnóstico: MELASMA FACIAL E EXTRAFACIAL\n\nConduta: zella\naplicar no rosto À noite e retirar pela manhã\natoderm baume 500ml\naplicar no corpo 2x/dia\natoderm gel creme\nAPLICAR NO CORPO 3-4X/DIA\nAnti-Pigment Creme Corporal para Áreas Específicas\nAplicar uma fina camada nas áreas com manchas 1-2 vezes ao dia	2026-02-28 02:01:51.150526	189
178	168	5	2026-02-03 10:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:51.277684	197
179	220	5	2026-02-11 15:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:51.404394	252
180	169	5	2026-02-03 11:00:00	Queixa principal: QS E\nCOCEIRA NO CORPO\n\nConduta: CETAPHIL E HIXIZINE	2026-02-28 02:01:51.533008	198
181	162	5	2026-02-03 11:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:51.661386	190
182	233	5	2026-02-12 15:00:00	Conduta: fez 2 transplante na coroa 2019 e 2020\nhj inico minoxidil oral e topico cabelo vem ficnado muito branco	2026-02-28 02:01:52.125619	266
183	252	5	2026-02-19 16:30:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nConduta: O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n\n\n📋 RECEITA EMITIDA:	2026-02-28 02:01:52.760598	289
184	243	5	2026-02-13 15:00:00	Queixa principal: Paciente refere queixa de rarefação capilar e calvície progressiva.\n\nConduta: O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	2026-02-28 02:01:53.142872	279
185	247	5	2026-02-19 10:00:00	Queixa principal: coceira no  corpo\n\nDiagnóstico: pruruido por estresse e ressecamento\n nao tem lesao de pele\n\nConduta: 📋 RECEITA EMITIDA:	2026-02-28 02:01:53.438816	283
186	267	5	2026-02-25 10:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: 📋 RECEITA EMITIDA:	2026-02-28 02:01:53.60829	307
187	307	5	2026-02-27 15:15:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:53.990323	351
188	302	5	2026-02-27 16:00:00	Exame/Anamnese: Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\nConduta: [Conduta registrada via procedimentos]	2026-02-28 02:01:54.116958	346
189	288	5	2026-02-26 16:00:00	Queixa principal: Retoque de Botox na glabela e testa.\n\nConduta: Realizado 25u de Botox. Retorno em 15 dias.	2026-02-28 02:21:38.550459	331
190	315	5	2026-03-02 18:04:12.358	fiz hj hialuronidase 10 u no labio inferior que tinha uma bolinha\ncorriji bem a assimetria porem esta mais inchado ainda com 30 dias depoois	2026-03-02 18:04:12.245181	359
192	160	5	2026-03-04 20:22:35.074	NL VERRUGA	2026-03-04 20:22:34.031316	187
193	307	5	2026-03-05 15:36:57.214	boa melhora da cicatrizeacao pos limeght ainda tem o padrao da ponteira faço peeling ar 3 horas	2026-03-05 15:36:57.30495	351
194	238	5	2026-03-09 13:56:37.783	NAO MELHOROU A QUESTOU DA TINHA PEDIS\nINICIOU ICACORT	2026-03-09 13:56:37.115985	271
195	105	5	2026-03-09 14:25:03.554	RETOQUE BOTOX	2026-03-09 14:25:02.859005	129
196	382	5	2026-03-12 12:21:00	faz hoje morpheus no cc\nface pescoco e colo	2026-03-12 12:21:54.087079	446
\.


--
-- Data for Name: follow_up_reminder; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.follow_up_reminder (id, patient_id, procedure_name, scheduled_date, reminder_type, status, notes, created_at) FROM stdin;
1	2	Ulthera	2026-05-24	cosmetic_follow_up	pending	\N	2025-11-25 18:52:40.900771
3	18	Botox	2026-05-31	cosmetic_follow_up	pending	\N	2025-12-02 12:51:15.266107
4	18	Peeling	2026-05-31	cosmetic_follow_up	pending	\N	2025-12-02 12:51:15.357541
5	21	Sculptra	2026-05-31	cosmetic_follow_up	pending	\N	2025-12-02 14:01:24.776632
6	33	Morpheus	2026-06-01	cosmetic_follow_up	pending	\N	2025-12-03 18:47:43.804037
7	34	Ulthera	2026-06-02	cosmetic_follow_up	pending	\N	2025-12-04 17:16:19.656024
8	34	Botox	2026-06-02	cosmetic_follow_up	pending	\N	2025-12-04 17:16:19.750357
9	36	Morpheus	2026-06-03	cosmetic_follow_up	pending	\N	2025-12-05 13:28:35.583127
10	36	Preenchimento	2026-06-03	cosmetic_follow_up	pending	\N	2025-12-05 13:28:35.671505
11	47	Morpheus	2026-06-07	cosmetic_follow_up	pending	\N	2025-12-09 18:10:25.665392
12	49	Radiesse	2026-06-07	cosmetic_follow_up	pending	\N	2025-12-09 19:09:48.803786
14	62	Morpheus	2026-04-10	cosmetic_follow_up	pending	\N	2025-12-11 15:16:39.015691
16	64	Morpheus	2026-06-09	cosmetic_follow_up	pending	\N	2025-12-11 18:33:23.135235
17	65	Morpheus	2026-06-09	cosmetic_follow_up	pending	\N	2025-12-11 19:19:03.093595
18	67	Ulthera	2026-06-10	cosmetic_follow_up	pending	\N	2025-12-12 12:41:57.688111
19	67	Outros	2026-10-08	cosmetic_follow_up	pending	\N	2025-12-12 12:41:57.68813
20	72	Botox	2026-06-10	cosmetic_follow_up	pending	\N	2025-12-12 17:36:36.823932
21	77	Sculptra	2026-06-10	cosmetic_follow_up	pending	\N	2025-12-12 18:56:35.497771
22	81	Morpheus	2026-06-10	cosmetic_follow_up	pending	\N	2025-12-12 19:56:09.428338
2	1	Profhilo	2026-05-26	cosmetic_follow_up	completed	\N	2025-11-27 23:02:34.31478
23	85	Ulthera	2026-06-13	cosmetic_follow_up	superseded	\N	2025-12-15 13:35:58.390288
24	85	Outros	2026-06-13	cosmetic_follow_up	superseded	\N	2025-12-15 13:35:58.390313
25	85	Ulthera	2026-06-13	cosmetic_follow_up	pending	\N	2025-12-15 13:42:15.533617
26	85	Outros	2026-06-13	cosmetic_follow_up	pending	\N	2025-12-15 13:42:15.533639
27	86	Morpheus	2026-06-13	cosmetic_follow_up	pending	\N	2025-12-15 18:58:15.350991
28	95	Botox	2026-06-14	cosmetic_follow_up	pending	\N	2025-12-16 18:32:45.154268
13	48	Sculptra	2026-06-07	cosmetic_follow_up	completed	\N	2025-12-09 19:16:08.324873
29	48	Sculptra	2026-06-15	cosmetic_follow_up	pending	\N	2025-12-17 14:07:04.54854
30	98	Pearl Fracionado	2026-07-18	cosmetic_follow_up	pending	\N	2026-01-19 17:26:46.640093
15	63	Ulthera	2026-06-09	cosmetic_follow_up	completed	\N	2025-12-11 17:59:53.853056
31	104	Ulthera	2026-07-20	cosmetic_follow_up	pending	\N	2026-01-21 14:47:13.61601
33	105	Pearl Fracionado	2026-07-20	cosmetic_follow_up	pending	\N	2026-01-21 18:30:00.551055
34	105	Morpheus	2026-07-20	cosmetic_follow_up	pending	\N	2026-01-21 18:30:00.551082
35	109	Morpheus	2026-07-20	cosmetic_follow_up	pending	\N	2026-01-21 20:23:14.000118
36	111	Ulthera	2026-07-20	cosmetic_follow_up	pending	\N	2026-01-21 20:24:43.251634
37	115	Peeling	2026-07-21	cosmetic_follow_up	pending	\N	2026-01-22 13:42:00.207014
38	121	Morpheus	2026-07-22	cosmetic_follow_up	pending	\N	2026-01-23 20:04:23.009798
39	128	Sculptra	2026-07-25	cosmetic_follow_up	pending	\N	2026-01-26 19:51:07.669247
40	130	Botox	2026-07-25	cosmetic_follow_up	pending	\N	2026-01-26 20:12:56.732252
41	136	Botox	2026-07-26	cosmetic_follow_up	pending	\N	2026-01-27 14:34:29.589319
42	136	Ulthera	2026-07-26	cosmetic_follow_up	pending	\N	2026-01-27 14:34:29.589367
44	156	Emtone	2026-08-01	cosmetic_follow_up	pending	\N	2026-02-02 19:57:33.04801
45	156	Preenchimento	2026-08-01	cosmetic_follow_up	pending	\N	2026-02-02 19:57:33.048035
46	168	Pearl Fracionado	2026-08-02	cosmetic_follow_up	pending	\N	2026-02-03 13:40:43.385342
47	168	Morpheus	2026-08-02	cosmetic_follow_up	pending	\N	2026-02-03 13:40:43.385368
48	170	Pearl Fracionado	2026-08-02	cosmetic_follow_up	pending	\N	2026-02-03 20:04:17.370761
49	175	Botox	2026-08-03	cosmetic_follow_up	pending	\N	2026-02-04 19:08:39.055789
50	177	Botox	2026-08-04	cosmetic_follow_up	pending	\N	2026-02-05 13:03:12.488159
51	177	Ulthera	2026-08-04	cosmetic_follow_up	pending	\N	2026-02-05 13:03:12.488182
52	180	Morpheus	2026-08-04	cosmetic_follow_up	pending	\N	2026-02-05 14:36:32.592111
53	180	Outros	2026-08-04	cosmetic_follow_up	pending	\N	2026-02-05 14:36:32.592139
54	180	Preenchimento	2026-08-04	cosmetic_follow_up	pending	\N	2026-02-05 14:36:32.592146
55	225	Preenchimento	2026-08-10	cosmetic_follow_up	pending	\N	2026-02-11 13:57:29.815274
56	225	Preenchimento	2026-08-10	cosmetic_follow_up	pending	\N	2026-02-11 13:57:29.815299
57	225	Ulthera	2026-08-10	cosmetic_follow_up	pending	\N	2026-02-11 13:57:29.815307
58	225	Peeling	2026-08-10	cosmetic_follow_up	pending	\N	2026-02-11 13:57:29.815313
62	228	Outros	2026-08-11	cosmetic_follow_up	pending	\N	2026-02-12 12:36:56.412422
63	239	Sculptra	2026-08-12	cosmetic_follow_up	pending	\N	2026-02-13 13:29:30.672784
64	239	Ulthera	2026-08-12	cosmetic_follow_up	pending	\N	2026-02-13 13:29:30.672863
65	262	Outros	2026-08-12	cosmetic_follow_up	pending	\N	2026-02-13 18:40:32.247437
66	248	Sculptra	2026-08-18	cosmetic_follow_up	pending	\N	2026-02-19 20:30:43.353493
32	103	Outros	2026-07-20	cosmetic_follow_up	superseded	\N	2026-01-21 18:04:37.32107
67	103	Outros	2026-08-19	cosmetic_follow_up	pending	\N	2026-02-20 18:59:27.356194
68	265	Peeling	2026-08-24	cosmetic_follow_up	pending	\N	2026-02-25 12:57:29.111954
69	265	PEQUENA CIRURGIA	2026-08-24	cosmetic_follow_up	pending	\N	2026-02-25 12:57:29.11198
70	268	Emtone	2026-08-24	cosmetic_follow_up	pending	\N	2026-02-25 14:06:01.185644
71	268	Sculptra	2026-08-24	cosmetic_follow_up	pending	\N	2026-02-25 14:06:01.185669
72	288	Botox	2026-08-27	cosmetic_follow_up	pending	\N	2026-02-28 19:56:17.745874
73	317	Ulthera	2026-08-29	cosmetic_follow_up	pending	\N	2026-03-02 19:27:59.204408
74	321	Ulthera	2026-08-30	cosmetic_follow_up	pending	\N	2026-03-03 12:52:06.138921
75	321	Botox	2026-08-30	cosmetic_follow_up	pending	\N	2026-03-03 12:52:06.13895
76	324	Preenchimento	2026-08-30	cosmetic_follow_up	pending	\N	2026-03-03 13:47:58.601425
77	324	Emsculpt Neo	2026-08-30	cosmetic_follow_up	pending	\N	2026-03-03 13:47:58.601463
78	324	Preenchimento	2026-08-30	cosmetic_follow_up	pending	\N	2026-03-03 13:47:58.601472
79	323	Botox	2026-08-30	cosmetic_follow_up	pending	\N	2026-03-03 14:04:21.19222
80	323	Preenchimento	2026-08-30	cosmetic_follow_up	pending	\N	2026-03-03 14:04:21.192251
81	323	Emsculpt Neo	2026-08-30	cosmetic_follow_up	pending	\N	2026-03-03 14:04:21.192259
82	328	PEQUENA CIRURGIA	2026-08-30	cosmetic_follow_up	pending	\N	2026-03-03 18:38:37.517856
83	328	Botox	2026-08-30	cosmetic_follow_up	pending	\N	2026-03-03 18:38:37.517881
84	328	Peeling	2026-08-30	cosmetic_follow_up	pending	\N	2026-03-03 18:38:37.517888
85	333	MD Codes	2026-08-30	cosmetic_follow_up	pending	\N	2026-03-03 20:31:55.742658
86	333	Sculptra	2026-08-30	cosmetic_follow_up	pending	\N	2026-03-03 20:31:55.742688
87	338	Botox	2026-08-31	cosmetic_follow_up	pending	\N	2026-03-04 13:42:55.947177
88	341	MD Codes	2026-08-31	cosmetic_follow_up	pending	\N	2026-03-04 15:00:02.22815
89	341	Peeling	2026-08-31	cosmetic_follow_up	pending	\N	2026-03-04 15:00:02.228176
90	341	Ulthera	2026-08-31	cosmetic_follow_up	pending	\N	2026-03-04 15:00:02.228197
91	347	Morpheus	2026-08-31	cosmetic_follow_up	pending	\N	2026-03-04 19:33:51.798014
92	347	PDRN	2026-08-31	cosmetic_follow_up	pending	\N	2026-03-04 19:33:51.798048
93	378	Botox	2026-09-02	cosmetic_follow_up	pending	\N	2026-03-06 14:24:35.874123
94	259	Outros	2026-09-05	cosmetic_follow_up	pending	\N	2026-03-09 13:14:16.195139
95	387	Ulthera	2026-09-05	cosmetic_follow_up	pending	\N	2026-03-09 20:25:43.201299
96	387	Botox	2026-09-05	cosmetic_follow_up	pending	\N	2026-03-09 20:25:43.201325
100	390	Ulthera	2026-09-06	cosmetic_follow_up	pending	\N	2026-03-10 13:07:18.446182
101	393	Morpheus	2026-09-06	cosmetic_follow_up	pending	\N	2026-03-10 18:40:59.954489
102	394	Botox	2026-09-06	cosmetic_follow_up	pending	\N	2026-03-10 18:52:43.242717
103	394	Ulthera	2026-09-06	cosmetic_follow_up	pending	\N	2026-03-10 18:52:43.242745
59	219	Pearl Fracionado	2026-08-10	cosmetic_follow_up	completed	\N	2026-02-11 18:11:35.393149
60	219	Sculptra	2026-08-10	cosmetic_follow_up	completed	\N	2026-02-11 18:11:35.393176
61	219	Botox	2026-08-10	cosmetic_follow_up	superseded	\N	2026-02-11 18:11:35.393184
104	219	Botox	2026-09-07	cosmetic_follow_up	pending	\N	2026-03-11 13:01:39.390667
97	382	Morpheus	2026-09-06	cosmetic_follow_up	completed	\N	2026-03-10 11:38:54.822087
98	382	Morpheus	2026-09-06	cosmetic_follow_up	completed	\N	2026-03-10 11:38:54.822106
99	382	Sculptra	2026-09-06	cosmetic_follow_up	superseded	\N	2026-03-10 11:38:54.822112
105	382	Morpheus	2026-09-08	cosmetic_follow_up	pending	\N	2026-03-12 12:22:11.511171
106	382	Sculptra	2026-09-08	cosmetic_follow_up	pending	\N	2026-03-12 12:22:11.511229
108	363	Botox	2026-09-08	cosmetic_follow_up	pending	\N	2026-03-12 17:59:08.824741
109	363	Preenchimento	2026-09-08	cosmetic_follow_up	pending	\N	2026-03-12 17:59:08.824769
110	363	Pearl Fracionado	2026-09-08	cosmetic_follow_up	pending	\N	2026-03-12 17:59:08.824777
111	224	Ulthera	2026-09-08	cosmetic_follow_up	pending	\N	2026-03-12 19:19:11.179228
112	224	Peeling	2026-09-08	cosmetic_follow_up	pending	\N	2026-03-12 19:19:11.179386
113	224	Botox	2026-09-08	cosmetic_follow_up	pending	\N	2026-03-12 19:19:11.179402
114	419	Botox	2026-09-08	cosmetic_follow_up	superseded	\N	2026-03-12 19:59:03.57934
115	419	Morpheus	2026-09-08	cosmetic_follow_up	superseded	\N	2026-03-12 19:59:03.579367
116	419	Botox	2026-09-08	cosmetic_follow_up	pending	\N	2026-03-12 19:59:14.902325
117	419	Morpheus	2026-09-08	cosmetic_follow_up	pending	\N	2026-03-12 19:59:14.902403
107	404	Preenchimento	2026-09-08	cosmetic_follow_up	superseded	\N	2026-03-12 12:44:38.672683
118	404	Preenchimento	2026-09-08	cosmetic_follow_up	pending	\N	2026-03-12 20:16:59.85568
119	404	Preenchimento	2026-09-08	cosmetic_follow_up	pending	\N	2026-03-12 20:16:59.85573
\.


--
-- Data for Name: hair_transplant; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.hair_transplant (id, note_id, norwood_classification, previous_transplant, transplant_location, case_type, number_of_surgeries, body_hair_needed, eyebrow_transplant, beard_transplant, frontal_transplant, crown_transplant, complete_transplant, complete_with_body_hair, surgical_planning, clinical_conduct, created_at, feminine_hair_transplant, dense_packing) FROM stdin;
1	7		nao		\N	1	f	f	f	f	f	t	f	frontal desenho conservador e coroa	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n	2025-11-27 18:06:51.308272	f	f
3	26	\N	nao	\N	\N	1	f	f	f	f	f	f	f	calvicie muito extensa\narea doadora ruim\npenso em 2500 capilar \n1000 barba e 2000 peito\n\nainda sim ficara ralo com desenho conservador	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n	2025-12-02 13:21:53.34137	f	f
4	36	\N	nao	\N	\N	1	f	f	f	f	f	f	f		calvicie grande coroa principal\nindco 50 frontal\ne 50 coroa\nfios finos\ndeixei claro q a coroa é insuficiente\nfazer hairline conservadora      \n	2025-12-03 20:06:05.922657	f	f
5	38	\N	nao	\N	\N	1	f	f	f	f	t	f	f	apenas coroa sem fazer frontal	transplnate coroa\n\n	2025-12-03 20:10:52.1616	f	f
6	45	\N	nao	\N	\N	1	f	f	f	f	f	t	f	cabelo branco fios finos	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n	2025-12-05 13:24:08.694394	f	f
7	52	\N	sim	outro_servico	\N	1	f	f	f	f	t	t	f		O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n	2025-12-05 13:39:08.785008	f	f
8	63	\N	nao	\N	\N	1	f	f	f	t	f	f	f	dense packing um pouco de escalpe medio\narea  doadora  muito boa	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n	2025-12-09 20:31:48.910716	f	f
9	65	\N	nao	\N	\N	1	f	f	f	t	f	f	f	frontal manter a hairline	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n	2025-12-09 20:33:50.018892	f	f
10	76	\N	nao	\N	\N	1	f	f	f	t	t	f	f	corora e dense packing	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n	2025-12-10 18:37:06.602626	f	f
11	80	\N	nao	\N	\N	1	f	f	f	f	f	f	f	fazer o transpalnte na menor area possivel\n areadoadora ruim\nmuito fino ralo pensei 2000-2500	fazer o transpalnte na menor area possivel\n areadoadora ruim\nmuito fino ralo pensei 2000-2500	2025-12-10 19:15:38.805397	f	f
12	120	\N	nao	\N	\N	1	f	f	f	t	f	f	f		O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n	2025-12-12 20:14:29.430974	f	t
13	136	\N	nao	\N	\N	1	f	f	f	f	f	t	f		O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n	2025-12-15 13:43:14.900554	f	f
14	140	\N	nao	\N	\N	1	f	f	f	f	f	t	f		O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n	2025-12-15 18:34:51.154936	f	f
15	165	\N	nao	\N	\N	1	f	f	f	t	f	f	f	foco total na frente escalpe e coroa pode segurar com medicamento	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n	2026-01-21 17:59:10.481527	f	f
16	171	\N	nao	\N	\N	1	f	f	f	f	f	t	f	CALVICIE EXTENSA DESENHO CONSERVADOR MANTER A HAIRLINE E A ENTRADA	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n	2026-01-21 19:27:47.803137	f	f
17	175	\N	nao	\N	\N	1	f	f	f	t	f	t	f	MELHORA DA HAIRLINE	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n	2026-01-21 20:22:19.622137	f	f
18	193	\N	nao	\N	\N	1	f	f	f	f	f	f	f		O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n	2026-01-23 19:22:54.445928	f	f
19	202	\N	nao	\N	\N	1	f	f	f	f	f	t	f	cabelo fino\ntem indicaçao de um anova ciruirgia	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n	2026-01-26 18:52:15.633878	f	f
20	208	\N	nao	\N	\N	1	f	f	f	f	f	t	f	PACIENTE TEM PRIORIDADE COROA	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\nFAZER 70 COROA E 30 FRONTAL SO ENTRADINHA  OU 60 40	2026-01-27 12:57:33.855817	f	f
21	235	\N	nao	\N	\N	1	f	f	f	f	f	t	f	60 frontal e 10 escalpe e 30 coroa\napesar de ter preferencia na coroa	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n	2026-01-27 19:10:30.640323	f	f
22	237	\N	nao	\N	\N	1	f	f	f	f	f	f	t	calvicie extensa\narea doadora pequena\nindico body hair ocm desenho bem conservador imaginei 2500 a 3 capilar e 2000 barba e pelo	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\nininciar tratamento depois	2026-01-27 20:13:20.886366	f	f
23	256	\N	nao	\N	\N	1	f	f	f	f	f	f	f		O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\ntiro foto 03/2/26\n\n	2026-02-03 13:06:16.992881	f	f
24	266	\N	nao	\N	\N	1	f	f	f	f	t	f	f		O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n	2026-02-03 18:16:43.308557	f	f
25	270	\N	nao	\N	\N	1	f	f	f	f	f	f	f		O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n🧾 PRESCRIÇÃO MÉDICA\n\nPaciente: ALEXANDRE VINICIUS DA SILVA PEREIRA\n\n💊 Uso Oral:\n- NEOSIL ATTACK\n  TOMAR 01 CP VO POR DIA POR 3 MESES\n- MINOXIDIL 2,5MG\n  TOMAR 01 CP VO POR DIA\n\n🧴 Uso Tópico:\n- CAPPY\n  APLICAR NO COURO CABELUDO 1X/DIA\n\nDr. Arthur Basile – CRM 125.217\nDermatologista\n\nClínica Basile – Av. Prof. João Fiúsa, 2300 – Ribeirão Preto – SP\nwww.clinicabasile.com.br | Fone/Fax: (16) 3602-7785	2026-02-04 12:59:51.426557	f	f
26	272	\N	nao	\N	\N	1	f	f	f	f	f	f	f	tem a hairline mantida cobrir as entradas	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\nminoxidil 2,5	2026-02-04 13:15:40.855999	f	t
27	284	\N	nao	\N	\N	1	f	f	f	f	f	f	f	PACIENTE QUER AUMENTO DE VOLUME E DIMNUICAO DA TESTA\n PRA FAZER SEM RASPAR DEVERIA FAZER SO AIRLINE NAO FAZER VOLUME	FINASTEIRDA 5MG JA TOMA MINOXIDIL ORAL\nORIENTACAO GERAL	2026-02-05 14:41:26.828674	f	f
28	291	\N	nao	\N	\N	1	f	f	f	f	f	f	f		O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n	2026-02-05 19:28:18.455214	f	f
29	295	\N	nao	\N	\N	1	f	f	f	f	f	f	f	PACIENTE MUITO  NOVO\nTEM MUITA ENTRADQA MAS NAO TRATA	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n🧾 PRESCRIÇÃO MÉDICA\n\nPaciente: DIOGO ARROYO\n\n💊 Uso Oral:\n- NEOSIL ATTACK\n  TOMAR 01 CP VO POR DIA POR 3 MESES\n- MINOXIDIL 2,5MG\n  TOMAR 01 CP VO POR DIA\n- FINASTERIDA 1MG\n  TOMAR 1 CP VO POR DIA\n\n🧴 Uso Tópico:\n- CAPPY\n  APLICAR NO COURO CABELUDO 1X/DIA\n\nDr. Arthur Basile – CRM 125.217\nDermatologista\n\nClínica Basile – Av. Prof. João Fiúsa, 2300 – Ribeirão Preto – SP\nwww.clinicabasile.com.br | Fone/Fax: (16) 3602-7785	2026-02-05 20:50:46.6564	f	t
30	313	\N	nao	\N	\N	1	f	f	f	f	t	f	f	na frente apenas detalhes 30%	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\niniciar trataqmento depois parou ha 2 anos	2026-02-11 20:14:34.215432	f	f
31	326	\N	sim	outro_servico	\N	1	f	f	f	f	f	t	f	ja tem um fut\narea dodaora para 3000 3500\nimpossivel cobrir tudo\ntentar body hair que sera so barba	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n	2026-02-13 18:38:59.152882	f	f
32	332	\N	nao	\N	\N	1	f	f	f	f	f	t	f	desenho conservador	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n	2026-02-19 13:20:21.812418	f	f
33	337	\N	nao	\N	\N	1	f	f	f	t	f	f	f		O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n\n\n📋 RECEITA EMITIDA:\n	2026-02-19 19:52:57.798857	f	f
34	339	\N	nao	\N	\N	1	f	f	f	f	f	f	f		O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n\n\n📋 RECEITA EMITIDA:\n	2026-02-19 20:11:11.755333	f	f
35	386	\N	nao	\N	primaria	1	f	f	f	t	t	f	f	Teste		2026-02-28 01:49:38.774296	f	f
36	438	\N	nao	\N	primaria	1	f	f	f	t	f	f	f	nao quer abaixar tanto a hairline\nfazer apartir do que tem e abaixar um pouco das entradas		2026-03-03 18:25:12.375675	f	f
37	468	\N	nao	\N	primaria	1	f	f	f	f	f	t	f	PRIORIDADE FRONTAL\nSazer hairline conservadora com  entrada\nchamar a esposa\npaciente quer 80 frontal e 20 cora\ntaçvez 60 40		2026-03-04 18:27:05.011765	f	f
38	470	\N	nao	\N	primaria	1	f	f	f	t	f	f	f	AREA DOADORA RUIM\nTEM AREA DOARA PARA BODY HAIR EM UMA POSSIVEL CIRURGIA		2026-03-04 19:06:10.324585	f	f
39	474	\N	nao	\N	primaria	1	f	f	f	f	t	f	f	PACIENTE TEM PRIORIDADE COROA\nFAZER 70 POR CENTO NA COROA\n30 NA HAIRLINE MANTENDO EXATAMETNE A LINHA SEM AUMENTAR ENTRADAS PACIENTE BEM CONSERVADOR		2026-03-04 19:57:40.297466	f	f
40	490	\N	sim	ICB	primaria	1	f	f	f	f	f	f	f	fazer o segundo abaixando a entrada e corrigindo o pico temporal tirei foto do desneho depois disso implemntar aumento da densidade na frente e 30 % a tras no maximo, apesar de precisar paciente quer prioridade frente e entradas		2026-03-05 19:48:29.825319	f	f
41	496	\N	nao	\N	primaria	1	f	f	f	t	f	f	f	alta densidade so na frente		2026-03-06 13:28:32.817858	f	f
42	525	\N	nao	\N	primaria	1	f	f	f	f	t	f	f	quer desenho bem agressivo	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n	2026-03-10 18:24:10.940805	f	f
43	535	3	nao	\N	primaria	1	f	f	f	f	f	t	f	manter a hairline tinha v pico de viuva\n\naumentar a densidade 60 frontal	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n\n\n📋 RECEITA EMITIDA:\n	2026-03-10 19:44:49.918408	f	f
44	539	3	nao	\N	primaria	1	f	f	f	f	f	t	f		O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n\n\n📋 RECEITA EMITIDA:\n	2026-03-11 13:21:35.688052	f	f
45	547	2	nao	\N	primaria	1	f	f	f	t	f	f	f	manter a hairline aumentar a densidade	ja usa finasterida	2026-03-11 15:26:54.001131	f	f
46	552	\N	nao	\N	primaria	1	f	f	f	f	f	t	f	quer um desenho bem agressivo\n mas ja esta precisando no escalpe  e coroa\n indico um densenho abaixando mais as entradas que a hairline\n70 frontal	inicio ja minoxidil oral\n\n📋 RECEITA EMITIDA:\n	2026-03-11 18:41:07.973864	f	f
47	554	3	nao	\N	primaria	1	f	f	f	f	f	t	f	fazer frontal abaixando 1 dedo coroa e fazer denso\ntambem o resto patchwork	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n	2026-03-11 19:13:25.099208	f	f
48	556	2	nao	\N	primaria	1	f	f	f	f	f	f	f		tem uma calvicie evidente na coroa\nmas nao se incomoda\ntem rarefacao na frente e ano se incomoda\nprefere iniciar tratamento\ntiro foto  na maquina\n\n📋 RECEITA EMITIDA:\n	2026-03-11 19:23:01.103302	f	f
49	564	\N	nao	\N	primaria	1	f	f	f	f	f	f	f		O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n	2026-03-12 13:44:44.304452	f	f
50	565	\N	nao	\N	primaria	1	f	f	f	f	f	f	f		\n\n📋 RECEITA EMITIDA:\n	2026-03-12 13:54:53.161043	f	f
\.


--
-- Data for Name: indication; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.indication (id, note_id, procedure_id, indicated, performed, created_at) FROM stdin;
\.


--
-- Data for Name: medication_usage; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.medication_usage (id, medication_id, prescribed_at) FROM stdin;
1	85	2025-12-12 20:26:50.436346
2	88	2026-02-06 18:00:58.032088
3	124	2026-02-11 19:31:03.663031
4	124	2026-02-12 20:04:50.627127
5	125	2026-02-12 20:09:18.236664
6	146	2026-02-12 20:38:30.994546
7	331	2026-02-12 20:38:31.124919
8	199	2026-02-12 20:38:31.206502
9	146	2026-02-12 20:43:57.809846
10	331	2026-02-12 20:43:57.895268
11	199	2026-02-12 20:43:57.978354
12	146	2026-02-12 20:45:58.880739
13	331	2026-02-12 20:45:58.971298
14	199	2026-02-12 20:45:59.059783
15	146	2026-02-12 20:48:28.515647
16	331	2026-02-12 20:48:28.606873
17	199	2026-02-12 20:48:28.705332
18	146	2026-02-13 14:27:20.046626
19	331	2026-02-13 14:27:20.14163
20	199	2026-02-13 14:27:20.230116
21	263	2026-02-19 13:28:06.821733
22	294	2026-02-19 13:28:06.94285
23	303	2026-02-19 13:59:35.766651
24	291	2026-02-19 14:42:53.50504
25	146	2026-02-19 19:49:46.029439
26	331	2026-02-19 19:49:46.144979
27	199	2026-02-19 19:49:46.258057
28	331	2026-02-19 20:10:23.566316
29	183	2026-02-19 20:10:23.675716
30	242	2026-02-19 20:10:23.785572
31	199	2026-02-19 20:10:23.895462
32	331	2026-02-20 14:26:25.3461
33	332	2026-02-25 12:52:50.360297
34	169	2026-02-25 12:52:50.45289
35	177	2026-02-25 12:52:50.539773
36	231	2026-02-25 13:22:30.660136
37	213	2026-02-25 14:02:56.799539
38	131	2026-02-25 14:02:56.889042
39	252	2026-02-25 14:02:56.979048
40	332	2026-02-25 14:23:24.840684
41	120	2026-02-25 14:23:24.928249
42	122	2026-02-25 14:23:25.015115
43	86	2026-02-25 14:23:25.103792
44	146	2026-02-25 17:48:03.887072
45	331	2026-02-25 17:48:03.97517
46	199	2026-02-25 17:48:04.061774
47	326	2026-02-25 18:14:43.752719
48	146	2026-02-26 13:16:21.261013
49	331	2026-02-26 13:16:21.355672
50	126	2026-02-26 13:16:21.443614
51	199	2026-02-26 13:16:21.533354
52	333	2026-02-26 13:16:21.621224
53	332	2026-02-26 14:00:26.242703
54	1	2026-02-26 14:00:26.334168
55	177	2026-02-26 14:00:26.420652
56	227	2026-02-26 14:00:26.508297
57	150	2026-02-26 14:00:26.595422
58	103	2026-02-26 14:11:39.192453
59	198	2026-02-26 14:11:39.286963
60	169	2026-02-27 13:20:45.468035
61	1	2026-02-27 13:20:45.549177
62	146	2026-02-27 13:56:20.459966
63	134	2026-02-27 13:56:20.552002
64	331	2026-02-27 14:14:53.815085
65	126	2026-02-27 14:14:53.904119
66	148	2026-02-27 14:14:53.993403
67	111	2026-02-27 14:14:54.082464
68	8	2026-02-27 15:00:19.090819
69	47	2026-02-27 15:00:19.184385
70	131	2026-02-27 15:00:19.274461
71	192	2026-02-27 15:00:19.364019
72	8	2026-02-27 15:03:48.120538
73	47	2026-02-27 15:03:48.21372
74	131	2026-02-27 15:03:48.30352
75	192	2026-02-27 15:03:48.3942
76	146	2026-02-27 19:41:28.209857
77	331	2026-02-27 19:41:28.298283
78	199	2026-02-27 19:41:28.383745
79	161	2026-03-02 13:31:43.62891
80	126	2026-03-02 20:08:02.900796
81	146	2026-03-03 12:37:21.829153
82	291	2026-03-03 12:37:21.929838
83	334	2026-03-03 12:37:22.021961
84	333	2026-03-03 12:37:22.11777
85	332	2026-03-03 12:37:22.208858
86	291	2026-03-03 13:06:52.924763
87	329	2026-03-03 13:46:08.414897
88	1	2026-03-03 13:46:08.506792
89	243	2026-03-03 13:46:08.592263
90	144	2026-03-03 14:14:18.679056
91	335	2026-03-03 14:14:18.819701
92	48	2026-03-03 14:14:18.912188
93	195	2026-03-03 14:36:33.951828
94	207	2026-03-03 14:36:34.041876
95	86	2026-03-03 14:36:34.13229
96	143	2026-03-03 15:14:15.666379
97	85	2026-03-03 15:14:15.755208
98	143	2026-03-03 15:33:36.271801
99	85	2026-03-03 15:33:36.358794
100	242	2026-03-03 18:23:01.843633
101	144	2026-03-03 18:23:01.934729
102	146	2026-03-03 18:51:19.011795
103	224	2026-03-03 18:51:19.109676
104	207	2026-03-03 18:51:19.200234
105	86	2026-03-03 18:51:19.294627
106	5	2026-03-03 20:33:13.586596
107	126	2026-03-04 12:45:52.515456
108	291	2026-03-04 12:45:52.608744
109	291	2026-03-04 13:12:08.662908
110	146	2026-03-04 13:12:08.754265
111	279	2026-03-04 13:12:08.842468
112	252	2026-03-04 13:38:16.714625
113	332	2026-03-04 14:51:46.569804
114	1	2026-03-04 14:51:46.661215
115	5	2026-03-04 14:51:46.750864
116	252	2026-03-04 14:51:46.840578
117	332	2026-03-04 18:00:06.220054
118	337	2026-03-04 18:00:06.311824
119	338	2026-03-04 18:00:06.398943
120	146	2026-03-04 18:24:00.405648
121	331	2026-03-04 18:24:00.502476
122	199	2026-03-04 18:24:00.594625
123	146	2026-03-05 14:11:35.013373
124	331	2026-03-05 14:11:35.11356
125	199	2026-03-05 14:11:35.201675
126	291	2026-03-05 19:06:23.199206
127	331	2026-03-05 19:33:55.043481
128	199	2026-03-05 19:33:55.133308
129	146	2026-03-05 19:45:51.587701
130	331	2026-03-05 19:45:51.678578
131	126	2026-03-05 19:45:51.769913
132	199	2026-03-05 19:45:51.861154
133	146	2026-03-06 13:21:07.050518
134	331	2026-03-06 13:21:07.140736
135	263	2026-03-06 13:21:07.228834
136	199	2026-03-06 13:21:07.316307
137	332	2026-03-06 14:21:34.695896
138	252	2026-03-06 14:21:34.783925
139	20	2026-03-06 14:21:34.871613
140	331	2026-03-09 13:25:19.073024
141	179	2026-03-09 13:41:07.68594
142	264	2026-03-09 13:56:52.90187
143	331	2026-03-09 14:14:23.233473
144	126	2026-03-09 14:14:23.324272
145	340	2026-03-09 14:14:23.410871
146	342	2026-03-09 14:14:23.549424
147	146	2026-03-09 19:55:06.233664
148	331	2026-03-09 19:55:06.337208
149	126	2026-03-09 19:55:06.425492
150	146	2026-03-09 20:09:18.467028
151	331	2026-03-09 20:09:18.559244
152	126	2026-03-09 20:09:18.657637
153	199	2026-03-09 20:09:18.755052
154	146	2026-03-10 18:00:06.822152
155	331	2026-03-10 18:00:06.919955
156	199	2026-03-10 18:00:07.007951
157	47	2026-03-10 18:40:34.457603
158	131	2026-03-10 18:40:34.550548
159	343	2026-03-10 18:52:18.813048
160	286	2026-03-10 18:52:18.899367
161	260	2026-03-10 18:52:18.985997
162	86	2026-03-10 19:09:50.545954
163	344	2026-03-10 19:09:50.63805
164	146	2026-03-10 19:41:58.547862
165	331	2026-03-10 19:41:58.639863
166	199	2026-03-10 19:41:58.735259
167	146	2026-03-11 13:21:11.699839
168	331	2026-03-11 13:21:11.794386
169	126	2026-03-11 13:21:11.880485
170	199	2026-03-11 13:21:11.966827
171	161	2026-03-11 13:35:41.934839
172	331	2026-03-11 18:40:22.500133
173	331	2026-03-11 19:22:31.575183
174	166	2026-03-12 12:34:35.075776
175	146	2026-03-12 13:51:35.03852
176	331	2026-03-12 13:51:35.130987
177	126	2026-03-12 13:51:35.222869
178	199	2026-03-12 13:51:35.562268
179	146	2026-03-12 18:56:37.624417
180	331	2026-03-12 18:56:37.719105
181	126	2026-03-12 18:56:37.806314
182	250	2026-03-12 18:56:37.894038
183	199	2026-03-12 18:56:37.981479
184	336	2026-03-12 19:55:35.925437
185	124	2026-03-12 19:55:36.021676
\.


--
-- Data for Name: medications; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.medications (id, name, purpose, type, brand, instructions, created_at) FROM stdin;
1	Anti-Pigment Dual Sérum	\N	topical	Eucerin	Clareamento de manchas e uniformização do tom da pele	2025-12-12 20:23:21.725029
2	Anti-Pigment Creme Facial Dia FPS 30	\N	topical	Eucerin	Redução de hiperpigmentação com proteção solar	2025-12-12 20:23:21.817319
3	Anti-Pigment Creme Facial Noite	\N	topical	Eucerin	Clareamento de manchas durante a noite	2025-12-12 20:23:21.905092
4	Anti-Pigment Creme para Mãos	\N	topical	Eucerin	Clareamento de manchas nas mãos	2025-12-12 20:23:21.993553
5	Anti-Pigment Creme Corporal para Áreas Específicas	\N	topical	Eucerin	Clareamento de manchas em áreas específicas do corpo	2025-12-12 20:23:22.080761
6	Anti-Pigment Creme Anti-Olheiras	\N	topical	Eucerin	Clareamento de olheiras	2025-12-12 20:23:22.167538
7	Hyaluron-Filler Creme Facial Dia FPS 30	\N	topical	Eucerin	Preenchimento de rugas e proteção solar	2025-12-12 20:23:22.254327
8	Hyaluron-Filler Creme Facial Noite	\N	topical	Eucerin	Preenchimento de rugas durante a noite	2025-12-12 20:23:22.342129
9	Hyaluron-Filler Creme para Contorno de Olhos FPS 15	\N	topical	Eucerin	Redução de rugas ao redor dos olhos	2025-12-12 20:23:22.428977
10	Hyaluron-Filler Elasticity Creme Facial Dia FPS 30	\N	topical	Eucerin	Melhora da elasticidade e preenchimento de rugas profundas	2025-12-12 20:23:22.515886
11	Hyaluron-Filler Elasticity Creme Facial Noite	\N	topical	Eucerin	Regeneração da pele e melhora da elasticidade	2025-12-12 20:23:22.602797
12	Hyaluron-Filler Elasticity 3D Sérum	\N	topical	Eucerin	Redução de manchas senis rugas profundas e melhora da elasticidade	2025-12-12 20:23:22.689603
13	Hyaluron-Filler Vitamin C Booster	\N	topical	Eucerin	Antioxidante para pele cansada e sem brilho	2025-12-12 20:23:22.777039
14	Sun Pigment Control FPS 60	\N	topical	Eucerin	Proteção solar e prevenção de manchas	2025-12-12 20:23:22.863616
15	Sun Oil Control Gel-Creme FPS 60	\N	topical	Eucerin	Proteção solar para pele oleosa com toque seco	2025-12-12 20:23:22.951754
16	Sun Oil Control Tinted Claro FPS 70	\N	topical	Eucerin	Proteção solar com cor para pele clara	2025-12-12 20:23:23.039152
17	Sun Oil Control Tinted Médio FPS 70	\N	topical	Eucerin	Proteção solar com cor para pele média	2025-12-12 20:23:23.126447
18	Sun Hydro Fluid FPS 60	\N	topical	Eucerin	Proteção solar ultraleve para todos os tipos de pele	2025-12-12 20:23:23.213856
19	Sun Photoaging Control FPS 50	\N	topical	Eucerin	Proteção solar com ação anti-idade	2025-12-12 20:23:23.300589
20	DermoPure Oil Control Gel de Limpeza	\N	topical	Eucerin	Limpeza profunda para pele oleosa e acneica	2025-12-12 20:23:23.387694
21	DermoPure Oil Control Sérum Efeito Triplo	\N	topical	Eucerin	Redução de acne oleosidade e marcas	2025-12-12 20:23:23.474639
22	DermoPure Oil Control Creme Corporal Efeito Triplo	\N	topical	Eucerin	Tratamento corporal para pele acneica	2025-12-12 20:23:23.560901
23	DermoPure Oil Control Ação Renovadora	\N	topical	Eucerin	Renovação celular e prevenção de acne	2025-12-12 20:23:23.647585
24	UreaRepair PLUS Loção Hidratante 10% Ureia	\N	topical	Eucerin	Hidratação intensa para pele extremamente seca	2025-12-12 20:23:23.73412
25	UreaRepair PLUS Creme para Pés 10% Ureia	\N	topical	Eucerin	Hidratação e reparação da pele dos pés	2025-12-12 20:23:23.82088
26	UreaRepair PLUS Creme para Mãos 5% Ureia	\N	topical	Eucerin	Hidratação e reparação da pele das mãos	2025-12-12 20:23:23.908303
27	pH5 Loção Hidratante	\N	topical	Eucerin	Hidratação e proteção da pele sensível	2025-12-12 20:23:23.994924
28	pH5 Gel de Limpeza	\N	topical	Eucerin	Limpeza suave para pele sensível	2025-12-12 20:23:24.081592
29	pH5 Óleo de Banho	\N	topical	Eucerin	Limpeza e hidratação durante o banho	2025-12-12 20:23:24.168403
30	Aquaphor Pomada Reparadora	\N	topical	Eucerin	Reparação intensiva da pele muito seca rachada ou irritada	2025-12-12 20:23:24.255345
31	Aquaphor Bálsamo Labial	\N	topical	Eucerin	Hidratação e reparação dos lábios secos e rachados	2025-12-12 20:23:24.342135
32	C E Ferulic	\N	topical	SkinCeuticals	Antioxidante com vitamina C para prevenir envelhecimento e melhorar firmeza	2025-12-12 20:23:24.431379
33	Phloretin CF	\N	topical	SkinCeuticals	Antioxidante com vitamina C e ácido ferúlico para uniformizar o tom da pele	2025-12-12 20:23:24.518604
34	Silymarin CF	\N	topical	SkinCeuticals	Antioxidante para peles oleosas e acneicas	2025-12-12 20:23:24.611473
35	Discoloration Defense	\N	topical	SkinCeuticals	Sérum clareador para reduzir manchas e melasma	2025-12-12 20:23:24.697641
36	Retinol 0.3 / 0.5 / 1.0	\N	topical	SkinCeuticals	Tratamento anti-idade com retinol para rugas e textura irregular	2025-12-12 20:23:24.786496
37	A.G.E. Interrupter	\N	topical	SkinCeuticals	Creme anti-idade para rugas profundas e perda de firmeza	2025-12-12 20:23:24.874085
38	Triple Lipid Restore 2:4:2	\N	topical	SkinCeuticals	Creme restaurador para barreira cutânea e hidratação intensa	2025-12-12 20:23:24.962193
39	Metacell Renewal B3	\N	topical	SkinCeuticals	Hidratante com niacinamida para melhorar textura e uniformizar o tom	2025-12-12 20:23:25.052093
40	Hydrating B5 Gel	\N	topical	SkinCeuticals	Sérum hidratante com ácido hialurônico e vitamina B5	2025-12-12 20:23:25.139649
41	Physical Fusion UV Defense SPF 50	\N	topical	SkinCeuticals	Protetor solar com cor e alta proteção UVA/UVB	2025-12-12 20:23:25.226602
42	Epidrat Corpo	\N	topical	Mantecorp	Hidratação intensiva para pele seca	2025-12-12 20:23:25.313525
43	Ivy C Gel	\N	topical	Mantecorp	Clareamento e prevenção do envelhecimento	2025-12-12 20:23:25.402109
44	Soapelle Sabonete	\N	topical	Mantecorp	Higiene corporal e controle de oleosidade	2025-12-12 20:23:25.488797
45	Ivy C AOX Gel	\N	topical	Mantecorp	Antioxidante com vitamina C para prevenção de sinais de envelhecimento	2025-12-12 20:23:25.57615
46	Ivy C10	\N	topical	Mantecorp	Creme anti-idade com vitamina C nanoencapsulada para rugas e firmeza	2025-12-12 20:23:25.662508
47	Reviline Retinol Sérum	\N	topical	Mantecorp	Sérum com retinol para renovação celular e redução de linhas finas	2025-12-12 20:23:25.749024
48	Glycare Sérum	\N	topical	Mantecorp	Sérum anti-idade com ácido glicólico para textura e luminosidade da pele	2025-12-12 20:23:25.83684
49	Epidrat Calm B5	\N	topical	Mantecorp	Hidratante calmante para peles sensíveis e sensibilizadas	2025-12-12 20:23:25.923816
50	Epidrat Mat FPS 30	\N	topical	Mantecorp	Hidratante facial matificante com proteção solar para peles oleosas	2025-12-12 20:23:26.010559
51	Episol Color FPS 70	\N	topical	Mantecorp	Protetor solar com cor disponível em diversos tons	2025-12-12 20:23:26.098474
52	Episol Sec Acqua FPS 60	\N	topical	Mantecorp	Protetor solar facial com toque seco e alta proteção	2025-12-12 20:23:26.185373
53	Episol Color Stick FPS 50	\N	topical	Mantecorp	Protetor solar em bastão com cor para reaplicação prática	2025-12-12 20:23:26.27284
54	Blancy TX	\N	topical	Mantecorp	Clareador facial para tratamento de hiperpigmentações	2025-12-12 20:23:26.360347
55	Toleriane Double Repair Moisturizer	\N	topical	La Roche-Posay	Hidratação e reparação da barreira cutânea	2025-12-12 20:23:26.447533
56	Cicaplast Baume B5	\N	topical	La Roche-Posay	Reparação de pele irritada e ressecada	2025-12-12 20:23:26.534477
57	Effaclar Duo (+)	\N	topical	La Roche-Posay	Tratamento de acne e imperfeições	2025-12-12 20:23:26.621294
58	Anthelios Melt-in Milk SPF 100	\N	topical	La Roche-Posay	Proteção solar de amplo espectro	2025-12-12 20:23:26.707569
59	Lipikar AP+ Balm	\N	topical	La Roche-Posay	Hidratação intensa para pele muito seca	2025-12-12 20:23:26.794821
60	Hyalu B5 Serum	\N	topical	La Roche-Posay	Preenchimento de rugas e hidratação	2025-12-12 20:23:26.886876
61	Retinol B3 Serum	\N	topical	La Roche-Posay	Redução de linhas finas e uniformização da pele	2025-12-12 20:23:26.974649
62	Glycolic B5 Serum	\N	topical	La Roche-Posay	Clareamento de manchas e renovação celular	2025-12-12 20:23:27.061562
63	Effaclar Adapalene Gel 0.1%	\N	topical	La Roche-Posay	Tratamento de acne com retinoide	2025-12-12 20:23:27.150506
64	Mela B3 Serum	\N	topical	La Roche-Posay	Clareamento de manchas escuras	2025-12-12 20:23:27.244616
65	Minéral 89	\N	topical	Vichy	Fortalecimento e hidratação da pele	2025-12-12 20:23:27.334285
66	LiftActiv Supreme	\N	topical	Vichy	Anti-idade e firmeza da pele	2025-12-12 20:23:27.421296
67	Normaderm PhytoAction	\N	topical	Vichy	Controle da acne e oleosidade	2025-12-12 20:23:27.510038
68	LiftActiv Vitamin C Serum	\N	topical	Vichy	Iluminação e uniformização do tom da pele	2025-12-12 20:23:27.596864
69	Aqualia Thermal	\N	topical	Vichy	Hidratação profunda e duradoura	2025-12-12 20:23:27.684574
70	Neovadiol Compensating Complex	\N	topical	Vichy	Cuidado para pele madura	2025-12-12 20:23:27.771912
71	Capital Soleil SPF 50	\N	topical	Vichy	Proteção solar facial	2025-12-12 20:23:27.85833
72	Pureté Thermale 3-in-1	\N	topical	Vichy	Limpeza tonificação e remoção de maquiagem	2025-12-12 20:23:27.945287
73	Slow Âge Fluid	\N	topical	Vichy	Prevenção de sinais de envelhecimento	2025-12-12 20:23:28.034909
74	Dercos Energizing Shampoo	\N	topical	Vichy	Fortalecimento capilar	2025-12-12 20:23:28.121538
75	Intensive Hyaluronic Cream	\N	topical	Institut Esthederm	Hidratação intensa e preenchimento de rugas e linhas finas com ácido hialurônico	2025-12-12 20:23:28.209006
76	Intensive Retinol Cream	\N	topical	Institut Esthederm	Correção de rugas profundas e renovação da pele com retinol	2025-12-12 20:23:28.297574
77	Intensive Vitamine C² Dual Concentrate	\N	topical	Institut Esthederm	Sérum antioxidante concentrado com 2x vitamina C para manchas e uniformização	2025-12-12 20:23:28.386012
78	Intensive Propolis+ Ácido Salicílico	\N	topical	Institut Esthederm	Sérum anti-imperfeições para pele oleosa e acneica	2025-12-12 20:23:28.474015
79	Intensive Propolis+ Ácido Ferúlico	\N	topical	Institut Esthederm	Antioxidante com efeito matte para peles oleosas e acneicas	2025-12-12 20:23:28.561607
80	Intensive Retinol Balm Rejuvenecedor de Olhos	\N	topical	Institut Esthederm	Contorno de olhos com retinol para reduzir rugas e linhas finas	2025-12-12 20:23:28.649919
81	Intensive Pro-Collagen+ Cream	\N	topical	Institut Esthederm	Creme firmador que estimula colágeno e redefine contornos faciais	2025-12-12 20:23:28.738947
82	Intensive Hyaluronic Serum	\N	topical	Institut Esthederm	Sérum hidratante com ácido hialurônico para pele desidratada	2025-12-12 20:23:28.825766
83	Intensive Vitamine C Gel-Cream	\N	topical	Institut Esthederm	Gel-creme com vitamina C para iluminar e uniformizar a pele	2025-12-12 20:23:28.913007
84	Intensive Spirulina Cream	\N	topical	Institut Esthederm	Creme revitalizante com spirulina para energizar a pele cansada	2025-12-12 20:23:28.999711
85	Minoxidil 5% solução capilar	\N	topical	\N	Aplicar 1mL na área afetada do couro cabeludo 2 vezes ao dia	2025-12-12 20:26:50.392902
86	isdin fusion water	\N	topical	\N	aplicar no rosto 2x/dia	2026-01-19 17:55:14.12638
87	ACNIBEN GEL SECATIVO	\N	topical	\N	APLICAR NAS REGIÕES AFETADAS 1-2X/DIA SE NECESSÁRIO	2026-02-02 15:16:32.434139
88	ADACNE	\N	topical	\N	aplicar no rosto À noite e retirar pela manhã	2026-02-02 15:16:32.525381
89	ADACNE CLIN	\N	topical	\N	Aplicar no rosto à noite e retirar pela manhã	2026-02-02 15:16:32.614212
90	AGUA MICELAR SEBIUM BIODERMA	\N	topical	\N	REMOVER A MAQUIAGEM SE NECESSÁRIO	2026-02-02 15:16:32.698892
91	ALOXEDIL	\N	topical	\N	APLICAR NO COURO CABELUDO 1X/DIA POR 6 MESES	2026-02-02 15:16:32.783207
92	AVENE RETRINAL 0,1	\N	topical	\N	aplicar no rosto À noite e retirar pela manhã	2026-02-02 15:16:32.867591
93	AVENE RETRINAL OIL CONTROL	\N	topical	\N	aplicar no rosto À noite e retirar pela manhã	2026-02-02 15:16:32.95252
94	AVENE RETRINAL OLHOS	\N	topical	\N	aplicar nas areas dos olhos 2x/dia	2026-02-02 15:16:33.03792
95	Acniben Spray Corporal Antiacne ISDIN	\N	topical	\N	aplicar nas costas À noite e retirar pela manhã	2026-02-02 15:16:33.124905
96	Amilia Repair - Loção Prebiótica	\N	topical	\N	aplicar no rosto 2x/dia	2026-02-02 15:16:33.210572
97	BACTRIN F	\N	oral	\N	Tomar 1cp vo de 12/12h por 7 dias	2026-02-02 15:16:33.722244
98	BLANCY 8 MANTECORP	\N	topical	\N	aplicar no rosto À noite e retirar pela manhã	2026-02-02 15:16:33.807148
99	BLANCY OLHOS	\N	topical	\N	aplicar nas areas dos olhos 2x/dia	2026-02-02 15:16:33.891834
100	CICAPLAST	\N	topical	\N	APLICAR NAS FERIDAS 5X/DIA	2026-02-02 15:16:34.060746
101	CICAPLAST LABIOS	\N	topical	\N	aplicar nos labios 4x/dia	2026-02-02 15:16:34.145012
102	CLINDOXYL GEL	\N	topical	\N	Aplicar no rosto à noite e retirar pela manhã	2026-02-02 15:16:34.230154
103	CLOBETASOL POMADA	\N	topical	\N	APLICAR NAS MAOS 1X/DIA À NOITE E OCLUIR COM LUVA	2026-02-02 15:16:34.316567
104	Cefadroxil 500 mg	\N	oral	\N	Tomar 1 cp vo 12/12horas por 7 dias	2026-02-02 15:16:34.443277
105	Cetaphil Optimal Hydration com Ácido Hialurônico - Creme	\N	topical	\N	aplicar no rosto 2x/dia	2026-02-02 15:16:34.527637
106	Cetaphil Pro AD Restoraderm Creme Hidratante	\N	topical	\N	aplicar no corpo 3x/dia	2026-02-02 15:16:34.612502
107	Creme Facial Diário Fisiogel A.I.	\N	topical	\N	APLICAR NO ROSTO 2-3X/DIA	2026-02-02 15:16:34.740165
108	Creme Facial Fisiogel - A.I. Diário	\N	topical	\N	aplicar no rosto 4x/dia	2026-02-02 15:16:34.825591
109	Creme Hidratante Facial Cetaphil Pro AR Calm Control	\N	topical	\N	aplicar no rosto 2x/dia	2026-02-02 15:16:34.91035
110	Creme Reparador Protetor Avène Cicalfate+	\N	topical	\N	aplicar nas feridas 1-2x/dia por 5 dias	2026-02-02 15:16:34.994702
111	DERCOS KERASOLUTION HIDRATANTE CAPILAR	\N	topical	\N	aplicar nos fios do cabelo após lavagem com shampo. 1x/semana	2026-02-02 15:16:35.078736
112	DERCOS PSOLUTION SHAMPO	\N	topical	\N	LAVAR O COURO CABELUDO 1X/DIA	2026-02-02 15:16:35.163361
113	DIPROGENTA	\N	topical	\N	APLICAR NAS FERIDAS 1X/DIA SE NECESSÁRIO POR 5 DIAS	2026-02-02 15:16:35.249748
114	DIPROGENTA POMADA	\N	topical	\N	APICAR NO COURO CABELUDO 2X/DIA	2026-02-02 15:16:35.335563
115	DIPROSALIC SOLUÇÃO	\N	topical	\N	APLICAR NAS LESOES 1X/DIA POR 10 DIAS REUTILIZAR SE NECESSÁRIO	2026-02-02 15:16:35.422561
116	DIPROSONE	\N	topical	\N	APLICAR NAS LESÕES 1X/DIA POR 5 DIAS	2026-02-02 15:16:35.544879
117	DIPROSPAN 1 AMPOLA	\N	oral	\N	APLICAR IM EM DOSE UNICA	2026-02-02 15:16:35.629542
118	Declaro, para os devidos fins, que a paciente ACIMA foi avaliada clinicamente e não apresenta doenças de pele no momento do exame.  Dessa forma, encontra-se apta para frequentar piscina, não havendo contraindicações dermatológicas.	\N	topical	\N	Aplicar uma fina camada na área afetada 1-2 vezes ao dia	2026-02-02 15:16:35.713559
119	EBASTEL 10MG	\N	oral	\N	TOMAR 1 CP VO POR DIA 7 DIAS	2026-02-02 15:16:36.069101
120	EFACLAR GEL CONCETRADO	\N	topical	\N	LAVAR O ROSTO 2X/DIA	2026-02-02 15:16:36.153684
121	ENDOFER 100MG	\N	oral	\N	TOMAR 1 CP MASTIGAVEL POR DIA POR 3 MESES	2026-02-02 15:16:36.238458
122	EPIDRAT CALM	\N	topical	\N	APLICAR NO ROSTO 3-4X/DIA	2026-02-02 15:16:36.326528
123	Espuma De Limpeza Facial Cetaphil Pro AR Calm Control	\N	topical	\N	LAVAR O ROSTO 2X/DIA	2026-02-02 15:16:36.712187
124	Esthederm Intensive Pro-Collagen+ - Creme	\N	topical	\N	aplicar no rosto À noite e retirar pela manhã	2026-02-02 15:16:36.797687
125	Esthederm Intensive Retinol Eye Lifting	\N	topical	\N	aplicar nas areas dos olhos 2x/dia	2026-02-02 15:16:36.882596
126	FINASTERIDA 1MG	\N	oral	\N	TOMAR 1 CP VO POR DIA	2026-02-02 15:16:36.969493
127	FLAVO C - ISDIN	\N	topical	\N	APLICAR PELA MANHÃ ANTES DO PROTETOR SOLAR	2026-02-02 15:16:37.05521
128	GRISEOFULVINA 250MG/5ML	\N	oral	\N	TOMAR 5ML POR DIA POR 6 SEMANAS	2026-02-02 15:16:37.139795
129	HALOBEX	\N	topical	\N	APLICAR NAS LESOES 1X/DIA POR 10 DIAS REUTILIZAR SE NECESSÁRIO	2026-02-02 15:16:37.31309
130	HYDROBOOST GEL DE LIMPEZA NEUTROGENA	\N	topical	\N	LAVAR O ROSTO 2X/DIA POR DIA	2026-02-02 15:16:37.398617
131	Hyaluron-Filler Sérum Epigenetic	\N	topical	\N	APLICAR NO ROSTO à NOITE E RETIRAR PELA MANHÃ	2026-02-02 15:16:37.782504
132	ISDIN FUSION WATER	\N	topical	\N	APLICAR NO ROSTO 2X/DIA	2026-02-02 15:16:37.95981
133	IXIUM OU MODIK	\N	topical	\N	APLICAR NO ROSTO À NOITE E RETIRAR PELA MANHÃ USAR DE SEGUNDA A SEXTA PARAR  SABADO E DOMINGO	2026-02-02 15:16:38.045658
134	KERASOLUTION MASCARA CAPILAR	\N	topical	\N	APLICAR  NOS FIOS 1X/SEMANA APÓS LAVAGEM COM SHAMPOO	2026-02-02 15:16:38.688059
135	LIMECICLINA	\N	oral	\N	Tomar 1cp vo uma vez ao dia por 30 dias	2026-02-02 15:16:38.772952
136	LIMECICLINA 300	\N	oral	\N	Tomar 1cp vo de 12/12h por 7 dias	2026-02-02 15:16:38.857848
137	LIMECICLINA 300MG	\N	oral	\N	Tomar 1cp vo uma vez ao dia por 30 dias	2026-02-02 15:16:38.942223
138	LIMECILINA 300MG	\N	oral	\N	Tomar 1cp vo de 12/12h por 15 DIAS	2026-02-02 15:16:39.027507
139	La Roche-Posay Pure Vitamin C12 Oil Control - Sérum Facial	\N	topical	\N	APLICAR NO ROSTO PELA MANHA ANTES DO FPS	2026-02-02 15:16:39.113999
140	Loção Corporal de Hidratação Intensa ISDIN - Ureadin 10	\N	topical	\N	aplicar no corpo 1x/dia	2026-02-02 15:16:39.327662
141	MELA B3 la roche	\N	topical	\N	aplicar no rosto À noite e retirar pela manhã	2026-02-02 15:16:39.414448
142	MINESOL CORPO 70	\N	topical	\N	aplicar no corpo 1x/dia	2026-02-02 15:16:39.499451
143	MINOXIDIL 1MG (USO CONTINUO)	\N	oral	\N	TOMAR 1 CP VO POR DIA	2026-02-02 15:16:39.583491
144	MINOXIDIL 2,5 MG	\N	oral	\N	TOMAR 1 CP VO POR DIA (USO CONTINUO)	2026-02-02 15:16:39.669514
145	Mantecorp Reviline Retinol	\N	topical	\N	aplicar no rosto À noite e retirar pela manhã	2026-02-02 15:16:39.754154
146	NEOSIL ATTACK	\N	oral	\N	TOMAR 1 CP VO POR DIA POR 3 MESES	2026-02-02 15:16:39.966988
147	NOURKRIN	\N	oral	\N	TOMAR 1 CP VO PELA MANHÃ E 1 CP VOI à NOITE POR 3 MESES	2026-02-02 15:16:40.05163
148	PANT SEC	\N	topical	\N	APLICAR NO COURO CABELUDO 1X/DIA à NOITE	2026-02-02 15:16:40.17923
149	PANTOGAR	\N	oral	\N	TOMAR 2CP VO POR DIA	2026-02-02 15:16:40.265036
150	PIELLUS SHAMPOO	\N	topical	\N	LAVAR O COURO CABELUDO 2-3X POR SEMANA	2026-02-02 15:16:40.349484
151	PURE C 12	\N	topical	\N	APLICAR NO ROSTO PELA MANHA ANTES DO FPS	2026-02-02 15:16:40.434313
152	Pantogar Resist Silício 10g	\N	oral	\N	tomar 1 sachet por dia (uso continuo)	2026-02-02 15:16:40.518745
153	Profuse Clareador intensivo	\N	topical	\N	aplicar no rosto À noite e retirar pela manhã	2026-02-02 15:16:40.688946
154	Profuse Retinal serum	\N	topical	\N	aplicar no rosto À noite e retirar pela manhã	2026-02-02 15:16:40.774244
155	Protetor Solar Facial Anti-Idade Fusion Water Age Repair isdin	\N	topical	\N	aplicar no rosto 2x/dia	2026-02-02 15:16:40.858542
156	Protetor Solar Isdin Eryfotona AK-NMSC FLUIDO	\N	topical	\N	APLICAR NO ROSTO 2X/DIA	2026-02-02 15:16:40.944769
157	RETINOL H.A BOOSTER LA ROCHE	\N	topical	\N	aplicar no rosto À noite e retirar pela manhã	2026-02-02 15:16:41.071097
158	Rifocina spray	\N	topical	\N	Aplicar no local indicado 2x/dia por 7 dias	2026-02-02 15:16:41.286696
159	STRIACTIVE DERMAGE	\N	topical	\N	APLICAR NAS ESTRIAS 1X/DIA	2026-02-02 15:16:41.372833
160	STRIACTIVE-DERMAGE	\N	topical	\N	APLICAR NAS AREAS AFETADAS 1X/DIA	2026-02-02 15:16:41.456837
161	SUNFRESH OIL CONTROL FPS80 NEUTROGENA	\N	topical	\N	APLICAR NO ROSTO 2X/DIA	2026-02-02 15:16:41.541501
162	Shingrix	\N	oral	\N	VACINA DA HERPES, APLICAR CONFORME ORIENTAÇÃO	2026-02-02 15:16:41.630809
163	Sérum  Cetaphil Optimal Hydration	\N	topical	\N	APLICAR NO ROSTO 1-2X/DIA	2026-02-02 15:16:42.055564
164	Sérum Corretor Facial Antiacne Avène Cleanance Comedomed	\N	topical	\N	aplicar no rosto À noite e retirar pela manhã	2026-02-02 15:16:42.141155
165	Sérum Rejuvenescedor Vichy - Liftactiv H.A. Epidermic Filler	\N	topical	\N	aplicar no rosto pela manhã antes do fps	2026-02-02 15:16:42.225854
166	TARFIC 0,1	\N	topical	\N	Aplicar no rosto à noite e retirar pela manhã	2026-02-02 15:16:42.31056
167	TOPISON	\N	topical	\N	APLICAR NAS LESOES 1X/DIA à NOITE POR 5 DIAS	2026-02-02 15:16:42.395666
168	UREIA\t\t\t--------------\t\t20% ACIDO SALICILICO\t\t\t--------------\t\t4% LACTATO DE AMONIO\t\t\t--------------\t\t12% CREME HIDRATANTE\t\t\t--------------\t\t250 G	\N	topical	\N	aplicar nos braços 1x/dia À noite	2026-02-02 15:16:42.565551
169	VITACIDPLUS	\N	topical	\N	APLICAR NOR OSTO à NOITE E RETIRAR PELA MANHÃ	2026-02-02 15:16:42.777048
170	Vichy Dercos Anticaspa Sérum	\N	topical	\N	aplicar no couro cabeludo 1x/dia	2026-02-02 15:16:42.862377
171	Zinco quelato ----------------------- 50 mg\t\t\t\t Pycnogenol -------------------------- 40 mg\t\t\t\t Glucosamina ----------------------- 50 mg\t\t\t\t NUTRICOLIN----------------------- 200 mg	\N	oral	\N	tomar 1cp vo por dia por 3 meses	2026-02-02 15:16:42.94685
172	Zinco quelato ----------------------- 50 mg Pycnogenol -------------------------- 40 mg Glucosamina ----------------------- 50 mg NUTRICOLIN----------------------- 200 mg--------------------BLOOME---------------500MG	\N	oral	\N	TOMAR 1 CP VO POR DIA POR 3 MESES	2026-02-02 15:16:43.031102
173	a.o.x eye skinceulticals	\N	topical	\N	APLICAR NAS AREAS DOS OLHOS 2X/DIA	2026-02-02 15:16:43.116355
174	acne proofing sabonete	\N	topical	NEUTROGENA	lavar o rosto 2x/dia	2026-02-02 15:16:43.200513
175	acneben secativo	\N	topical	\N	aplicar nas espinhas 2x/dia	2026-02-02 15:16:43.284954
176	actine sabonete	\N	topical	\N	lavar o rosto 2x/dia	2026-02-02 15:16:43.369572
177	actine vitamina c	\N	topical	ACTINE	aplicar pela masnhã antes do protetor	2026-02-02 15:16:43.456503
178	ad 01 principia	\N	topical	\N	aplicar na virilha e na regiao dos seios 3x/semana	2026-02-02 15:16:43.540601
179	advatan	\N	topical	\N	aplicar nas lesoes 1x/dia por 5 dias	2026-02-02 15:16:43.625477
180	agua micelar sebium bioderma	\N	topical	\N	usar conforme orientação medica	2026-02-02 15:16:43.710687
181	agua micelar sensibio	\N	topical	\N	limpar o rosto se usar a maquiagem	2026-02-02 15:16:43.794995
182	allegra 180mg	\N	oral	\N	tomar 1 cp vo por di apor 7 dias	2026-02-02 15:16:43.879163
183	anacaps activ	\N	oral	\N	TOMAR 1 CP VO POR DIA POR 3 MESES	2026-02-02 15:16:43.964344
184	anthelios airlicium	\N	topical	\N	aplicar no rosto 2x/dia	2026-02-02 15:16:44.048969
185	anthelios anti idade	\N	topical	\N	aplicar no rosto 2x/dia	2026-02-02 15:16:44.134118
186	anthelios uv air	\N	topical	\N	aplicar no rosto 1-2x/dia	2026-02-02 15:16:44.218549
187	aquaphor labial	\N	topical	\N	aplica rnos labios 4-5x/dia	2026-02-02 15:16:44.387975
188	aquaphor labios/cicaplast labios/ bepantol labios	\N	topical	\N	aplicar nos labios 4x/dia	2026-02-02 15:16:44.472729
189	aquaphor pomada	\N	topical	\N	Tomar conforme orientação médica	2026-02-02 15:16:44.559442
190	asepxia sabonte enxofre	\N	topical	\N	lavar o corpo 1x/semana	2026-02-02 15:16:44.644421
191	atoderm baume 500ml	\N	topical	\N	aplicar no corpo 2x/dia	2026-02-02 15:16:44.729939
192	atoderm gel creme	\N	topical	\N	APLICAR NO CORPO 3-4X/DIA	2026-02-02 15:16:44.816276
193	atoderm oleo de banho	\N	topical	\N	lavar o corpo 1-2x/dia	2026-02-02 15:16:44.901764
194	avene gel de limpeza profunda	\N	topical	\N	lavar o rosto 2x/dia	2026-02-02 15:16:44.986949
195	azelan gel	\N	topical	\N	aplicar no rosto À noite e retirar pela manhã	2026-02-02 15:16:45.073636
196	bactrin f	\N	oral	\N	Tomar 1cp vo de 12/12h por 10 dias	2026-02-02 15:16:45.158562
197	bactrinf	\N	oral	\N	Tomar 1cp vo de 12/12h por 7 dias	2026-02-02 15:16:45.244138
198	bepantol baby	\N	topical	\N	aplicar  nos labios para dormir	2026-02-02 15:16:45.328979
199	cappy	\N	topical	\N	APLICAR NO COURO CABELUDO 1X/DIA à NOITE	2026-02-02 15:16:45.413911
200	cerave olhos	\N	topical	\N	aplicar nas areas dos olhos 2x/dia	2026-02-02 15:16:45.498976
201	cerave rosto	\N	topical	\N	aplicar no rosto 2-3x/dia	2026-02-02 15:16:45.59481
202	cetaphil health radiance -anti manchas	\N	topical	\N	aplicar no rosto pela manhã antes do fps	2026-02-02 15:16:45.683319
203	cetaphil percting serum anti manchas	\N	topical	\N	APLICAR NO ROSTO à NOITE E RETIRAR PELA MANHÃ	2026-02-02 15:16:45.768499
204	cetoconazol 200mg	\N	oral	\N	tomar 1 cp vo por dia por 15 dias	2026-02-02 15:16:45.863792
205	cetoconazol shampoo	\N	topical	\N	lavar o couro cabeludo 2x/semana	2026-02-02 15:16:45.948424
206	cicaplast serum reparador	\N	topical	\N	aplicar no rosto 1-2x/dia	2026-02-02 15:16:46.033516
207	cleanance gel	\N	topical	AVENE	LAVAR O ROSTO 2X/DIA	2026-02-02 15:16:46.120964
208	clindoxygel	\N	topical	\N	Aplicar no rosto à noite e retirar pela manhã	2026-02-02 15:16:46.205968
209	clindoxyl gel	\N	topical	\N	APLICAR NO ROSTO à NOITE E RETIRAR PELA MANHÃ	2026-02-02 15:16:46.29236
210	clob-x shampoo	\N	topical	\N	aplicar no couro cabeludo seco 1x/dia deixar por 20 min e depois enxaguar	2026-02-02 15:16:46.377287
211	clobetasol pomada	\N	topical	\N	Aplicar uma fina camada na área afetada 1-2 vezes ao dia	2026-02-02 15:16:46.462377
212	clobx shampoo	\N	topical	\N	aplicar no couro cabeludo seco deixar por 20 min e depois enxaguar	2026-02-02 15:16:46.546862
213	collagen h.a mantecorp	\N	oral	Mantecorp	tomar 1 sachet por dia por 3 meses	2026-02-02 15:16:46.631213
214	collagen specialist	\N	topical	\N	aplicar no rosto À noite e retirar pela manhã	2026-02-02 15:16:46.718855
215	collagen specialist 16 creme	\N	topical	\N	aplicar no rosto À noite e retirar pela manhã	2026-02-02 15:16:46.80436
216	collagen specialist 16 olhos vichy	\N	topical	\N	aplicar nas areas dos olhos 2x/dia	2026-02-02 15:16:46.889177
217	collagen specialist 16 serum	\N	topical	\N	aplicar no rosto À noite e retirar pela manhã	2026-02-02 15:16:46.97405
218	collagen specialist 16 vichy serum	\N	topical	\N	aplicar no rosto À noite e retirar pela manhã	2026-02-02 15:16:47.058274
219	comedomed	\N	topical	\N	aplicar no rosto À noite e retirar pela manhã	2026-02-02 15:16:47.142791
220	darrow sensinol	\N	oral	\N	LAVAR O COURO CABELUDO 1X/DIA	2026-02-02 15:16:47.227429
221	dercos condicionador	\N	topical	\N	aplicar apos lavagem co shampoo 3x/semana	2026-02-02 15:16:47.31185
222	dercos micropeel	\N	topical	\N	lavar o couro cabeludo 2x/semana	2026-02-02 15:16:47.398251
223	dercos psolution shampoo	\N	topical	\N	lavar o cabelo  diariamente	2026-02-02 15:16:47.482889
224	derivamicro	\N	topical	\N	APLICAR NO ROSTO à NOITE E RETIRAR PELA MANHÃ	2026-02-02 15:16:47.567701
225	dermapure serum	\N	topical	\N	aplicar no rosto pela manhã antes do fps	2026-02-02 15:16:47.652295
226	dermomax	\N	topical	\N	lavar o rosto 2x/dia	2026-02-02 15:16:47.736848
227	dermotivin original	\N	topical	\N	lavar o rosto 2x/dia	2026-02-02 15:16:47.823132
228	dermotivin soft	\N	topical	\N	lavar o rosto 2x/dia	2026-02-02 15:16:47.908608
229	desnsfiant fondant	\N	topical	\N	aplicar no rosto a noite e retirar pela manhã	2026-02-02 15:16:47.993224
230	desodorante la roche pele sensivel	\N	topical	\N	aplicar nas axilas 2x	2026-02-02 15:16:48.077505
231	diferin 0,3	\N	topical	\N	APLICAR NO ROSTO à NOITE E RETIRAR PELA MANHÃ	2026-02-02 15:16:48.16171
232	diprogenta	\N	topical	\N	aplicar 2x/dia por 5 dias	2026-02-02 15:16:48.247048
233	diprogenta pomada	\N	topical	\N	aplicar nas lesoes 2x/dia por 10 dias	2026-02-02 15:16:48.332172
234	diprosalic pomada	\N	topical	\N	aplicar nas lesoes 1x/dia por 30 dias parar 10 dias e reutilizar	2026-02-02 15:16:48.4187
235	diprosalic solução	\N	topical	\N	aplicar nas espinhas 2x/dia por uns 5 dias	2026-02-02 15:16:48.502976
236	diprosone	\N	topical	\N	aplicar na orelha 1x/dia por 7 dias	2026-02-02 15:16:48.587321
237	diprospan 1 ampola	\N	oral	\N	aplicar im em dose unica	2026-02-02 15:16:48.671482
238	diprospan im	\N	oral	\N	tomar im em dose unica	2026-02-02 15:16:48.755941
239	doctar plus	\N	topical	\N	lavar o couro cabeludo 2-3x/semana	2026-02-02 15:16:48.841286
240	doctar salic shampoo	\N	topical	\N	lavar o couro cabeludo 1-2x/semana	2026-02-02 15:16:48.92597
241	doxaciclina 100mg	\N	oral	\N	Tomar 1cp vo de 12/12h por 15 dias	2026-02-02 15:16:49.010961
242	dutasterida 0,5mg	\N	oral	\N	tomar 1 cp vo  3 x/semana	2026-02-02 15:16:49.095916
243	efaclar alta tolerancia	\N	topical	\N	lavar o rosto 2x/dia	2026-02-02 15:16:49.180606
244	efaclar concetrado	\N	topical	\N	lavar o rosto 2x/dia	2026-02-02 15:16:49.266067
245	efaclar duo m	\N	topical	\N	APLICAR NO ROSTO 1-2X/DIA	2026-02-02 15:16:49.351845
246	efaclar serum	\N	topical	\N	aplicar no rosto À noite e retirar pela manhã	2026-02-02 15:16:49.43606
247	endofer	\N	oral	\N	Tomar conforme orientação médica	2026-02-02 15:16:49.520876
248	epidrat calm	\N	topical	\N	aplicar no rosto 2-3x/dia	2026-02-02 15:16:49.605169
249	epiduo 0,3	\N	topical	\N	aplicar no rosto À noite e retirar pela manhã	2026-02-02 15:16:49.689901
250	espironolactona 100mg	\N	oral	\N	tomar 1 cp vo por dia (uso continuo)	2026-02-02 15:16:49.774373
251	espironolactona 200mg	\N	oral	\N	Tomar 1cp vo uma vez ao dia pela manhã	2026-02-02 15:16:49.858695
252	essencele c 20	ACHE	topical	\N	APLICAR NO ROSTO PELA MANHA ANTES DO FPS	2026-02-02 15:16:49.945128
253	eucerin actinic fluid	\N	topical	\N	aplicar no rosto 2x/dia	2026-02-02 15:16:50.032519
254	fentizol spray	\N	topical	\N	Aplicar uma fina camada na área afetada 1-2 vezes ao dia	2026-02-02 15:16:50.117138
255	finasterida 1mg	\N	oral	\N	Tomar conforme orientação médica	2026-02-02 15:16:50.201333
256	fisiogel ai 400ml	\N	topical	\N	APLICAR NO CORPO 1-2X/DIA	2026-02-02 15:16:50.285444
257	flavo c forte	\N	topical	\N	APLICAR NO ROSTO PELA MANHA ANTES DO FPS	2026-02-02 15:16:50.370612
258	glicoisdin 25	\N	topical	\N	aplicar no rosto À noite e retirar pela manhã	2026-02-02 15:16:50.455024
259	glycolic b5 serum la roche	\N	topical	\N	aplicar no rosto À noite e retirar pela manhã	2026-02-02 15:16:50.540086
260	health renew ceaphil	\N	topical	\N	aplicar no rosto À noite e retirar pela manhã	2026-02-02 15:16:50.624373
261	herpestal 500mg	\N	oral	\N	tomar 1 cp vo por dia 12/12 horas	2026-02-02 15:16:50.709638
262	hidroxicloroquina 400mg	\N	oral	\N	tomar 1 cp vo por dia (uso continuo)	2026-02-02 15:16:50.793913
263	hixizine 25mg	\N	oral	\N	TOMAR 1 CP VO POR DIA 2 HORAS ANTES DE DORMIR	2026-02-02 15:16:50.878297
264	icacort	\N	topical	\N	aplicar 2x/dia  NAS LESOES POR 10 DIAS	2026-02-02 15:16:50.962654
265	icaden spray	\N	topical	\N	aplicar no corpo 2x/dia por 15 dias	2026-02-02 15:16:51.048071
266	ideal soleil clarify	\N	topical	\N	aplicar no rosto 2x/dia	2026-02-02 15:16:51.133166
267	isdin fotoultra redness	\N	topical	\N	aplicar no rosto 2x/dia	2026-02-02 15:16:51.217594
268	isdin fusion water magic glow	\N	topical	\N	aplicar no rosto 1-2x/dia	2026-02-02 15:16:51.343832
269	isdin night concetrate	\N	topical	\N	aplicar no rosto À noite e retirar pela manhã	2026-02-02 15:16:51.428957
270	isdin reparador labial	\N	topical	\N	aplicar nos labios 4x/dia	2026-02-02 15:16:51.513502
271	isdin si nails	\N	topical	\N	aplicar nas unas 1x/dia por 30 dias	2026-02-02 15:16:51.5979
272	isdin spray pos sol	\N	topical	\N	aplicar  nas areas afetadas 1-2x/dia	2026-02-02 15:16:51.682244
273	isotretinoína 20mg	\N	oral	\N	tomar 02 cp vo por 30 dias na hora do almoço	2026-02-02 15:16:51.766746
274	ivcy c corpo	\N	topical	\N	APLICAR NO PESCOCO E COLO 1-2X/DIA	2026-02-02 15:16:51.852301
275	ivermecitna 6mg	\N	oral	\N	tomar 1 cp vo dose unica, e repetir o uso após 7 dias	2026-02-02 15:16:51.936772
276	ivy c corpo	\N	topical	\N	aplicar no colo 1-2x/dia	2026-02-02 15:16:52.021668
277	k-ox eye	\N	topical	\N	aplicar nas areas dos olhos 2x/dia	2026-02-02 15:16:52.106607
278	kelual ds	\N	topical	\N	LAVAR O COURO CABELUDO 3X/SEMANA	2026-02-02 15:16:52.191635
279	kerasoluiton mascara capilar	\N	topical	\N	APLICAR NOS FIOS DO CABELO 1X/SEMANA APÓS LAVAGEM COM SHAMPOO	2026-02-02 15:16:52.275958
280	kerium ds	\N	topical	\N	lavar o couro cabeludo 2x/semana	2026-02-02 15:16:52.359839
281	lapis secatriz	\N	topical	\N	aplicar nas espinhas 2x/dia	2026-02-02 15:16:52.445216
282	limeciclina 300mg	\N	oral	\N	Tomar 1cp vo de 12/12h por 15 dias	2026-02-02 15:16:52.566474
283	limeciclina 300mg (45cp)	\N	oral	\N	Tomar 1cp vo de 12/12h por 15 dias depois 1 cp vo por dia por mais 15 dias	2026-02-02 15:16:52.651897
284	limecilina 300 mg	\N	oral	\N	Tomar 1cp vo uma vez ao dia por 30 dias	2026-02-02 15:16:52.736414
285	limecilina 300mg	\N	oral	\N	Tomar 1cp vo de 12/12h por 30 dias	2026-02-02 15:16:52.820928
286	loceryl esmalte	\N	topical	\N	aplicar nas unhas 1x/semana após lixamento	2026-02-02 15:16:52.905711
287	loratadina 10mg	\N	oral	\N	tomar 1 cp vo por di apor 7 dias	2026-02-02 15:16:53.07474
288	mela b3 sabonete	\N	topical	\N	lavar o rosto 2x/dia	2026-02-02 15:16:53.161186
289	metotrexato 2,5mg	\N	oral	\N	tomar 1 cp vo por dia (uso continuo)	2026-02-02 15:16:53.246618
290	micolamina esmalte	\N	topical	\N	aplicar nas unhas 1x/semana após lixamento	2026-02-02 15:16:53.331266
291	minoxidil 0,5 mg	\N	oral	\N	Tomar 1cp vo uma vez ao dia	2026-02-02 15:16:53.41559
292	minoxidil 1,5mg	\N	oral	\N	tomar 1 cp vo por dia (uso continuo)	2026-02-02 15:16:53.503356
293	modik	\N	topical	\N	aplicar nas lesoes 1x/dia de segunda a sexta e parar sabado e domingo, utilizar por 4 semanas	2026-02-02 15:16:53.589797
294	neutrogena formula norueguesa	\N	topical	\N	aplicar no corpo se coceira	2026-02-02 15:16:53.674043
295	neutrogena sunfresh derma	\N	topical	\N	aplicar no rosto 2x/dia	2026-02-02 15:16:53.759377
296	normaderm gel	\N	topical	\N	lavar o rosto 2x/dia	2026-02-02 15:16:53.844237
297	nourkrin	\N	oral	\N	tomar 1 cp vo 12/12 horas por 3 meses	2026-02-02 15:16:53.929224
298	nouve corpo	\N	topical	\N	tomar 1 sachet por dia	2026-02-02 15:16:54.013464
299	nutrel b5	\N	topical	\N	aplicar na ferida 2x/dia por 1 semana	2026-02-02 15:16:54.097863
300	pantogar resist silicio	\N	oral	\N	tomar 1 sachet por dia por 3 meses	2026-02-02 15:16:54.31258
301	perspirex	\N	topical	\N	aplicar à noite 3-5x/semana	2026-02-02 15:16:54.397557
302	predsin	\N	oral	\N	Tomar 1cp vo uma vez ao dia por 7 dias	2026-02-02 15:16:54.481219
303	predsin 20mg	\N	oral	\N	tomar 3 cp vo por dia por 3 dias, depois 2 cp vo por mais 4 dias, depois 1 cp vo por mais 3 dias	2026-02-02 15:16:54.567157
304	predsin 40mg	\N	oral	\N	Tomar 1cp vo uma vez ao dia por 7 dias	2026-02-02 15:16:54.651329
305	probiatop	\N	oral	\N	tomar 1  sachet por dia por 3 meses	2026-02-02 15:16:54.741197
306	pure niacinamide 10	\N	topical	\N	aplicar no rosto pela manhã antes do fps	2026-02-02 15:16:54.825636
307	pure retinol serum vichy	\N	topical	\N	aplicar no rosto À noite e retirar pela manhã	2026-02-02 15:16:54.910194
308	pure vitamin c10	\N	topical	\N	aplicar  no rosto pela manhã antes do fps	2026-02-02 15:16:55.00082
309	rozex	\N	topical	\N	Aplicar no rosto à noite e retirar pela manhã	2026-02-02 15:16:55.085241
310	secatriz tonica rosada dermage	\N	topical	\N	aplicar no rosto deixar por 2 horas e enxaguar	2026-02-02 15:16:55.169923
311	selenio 2,5%-----------------------Shampoo base infantil suave (pH ~5,0–5,5), SLES ou anfótero (cocamidopropil betaína) + agente suspensor (xantana, carbômero neutralizado ou Veegum)----------------------30 ml	\N	topical	\N	lavar o couro cabeludo 1x/dia	2026-02-02 15:16:55.254451
312	shampoo dercos anti caspa	\N	topical	\N	lavar o couro cabeludo 2-3x/semana	2026-02-02 15:16:55.340248
313	solaquin	\N	topical	\N	aplicar no rosto todo junto com acido azelaico, lavar pela manhã e usar ate final de agosto	2026-02-02 15:16:55.426629
314	suavie sabonete	\N	topical	\N	lavar o rosto 2x/dia	2026-02-02 15:16:55.510996
315	suavie sabonete liquido	\N	topical	\N	lavar o rosto 2x/dia	2026-02-02 15:16:55.595274
316	tarfic 0,1	\N	topical	\N	aplicar nas descamações 1x/dia por 10 dias	2026-02-02 15:16:55.68017
317	therapsor solucao	\N	topical	\N	aplicar  8 -10 gotas na regiao afetada 1 x/dia por 5 dias reutilizar se necessa´rio	2026-02-02 15:16:55.765019
318	therapsor solução	\N	topical	\N	aplicar nas espinhas 1x/dia por 10 dias reutilizar se necessário	2026-02-02 15:16:55.853801
319	topison	\N	topical	\N	aplicar nas escamas 1x/dia por 5 dias	2026-02-02 15:16:55.938038
320	triple firming neck neostrata	\N	topical	\N	aplicar pescoco e colo À noite	2026-02-02 15:16:56.022647
321	ureadin 20	\N	topical	\N	APLICAR NOS PES 3-4X/DIA	2026-02-02 15:16:56.107239
322	ureadin cream 10	\N	topical	\N	aplicar nas pernas 1-2x/dia	2026-02-02 15:16:56.192184
323	ureadin mãos	\N	topical	\N	APLICAR NAS MAOS 3-4X/DIA	2026-02-02 15:16:56.276256
324	ureadin pes	\N	topical	\N	aplicar nos pes 1-2x/dia	2026-02-02 15:16:56.360415
325	valaciclovir 500mg	\N	oral	\N	tomar 1 cp vo 12/12 horas por 15 dias	2026-02-02 15:16:56.446971
326	verrux	\N	topical	\N	aplicar em cima das verrugas 1x/dia	2026-02-02 15:16:56.53225
327	vitacidplus	\N	topical	\N	aplicar no rosto À noite e retirar pela manhã	2026-02-02 15:16:56.616655
328	vitanol 0,5	\N	topical	\N	aplicar com cotonete nas estrias 3x/semana	2026-02-02 15:16:56.701584
329	zella	\N	topical	\N	aplicar no rosto À noite e retirar pela manhã	2026-02-02 15:16:56.786172
330	health renew serum facial-cetaphil	\N	topical	\N	aplicar no rosto pela manhã antes do fps	2026-02-02 18:36:05.468554
331	MINOXIDIL 2,5MG	\N	oral	\N	TOMAR 01 CP VO POR DIA	2026-02-12 20:38:31.080312
332	RETINOL BOOST NEUTROGENA	\N	topical	\N	aplicar no rosto À noite e retirar pela manhã	2026-02-25 12:52:28.437864
333	vitacid 0,025	\N	topical	\N	aplicar no couro cabeludo 1x/dia à noite e lavar pela manhã	2026-02-26 13:16:19.101826
334	Shampoo Anticaspa Pielus DI	\N	topical	\N	lavar o couro cabeludo 3x/semana	2026-03-03 12:35:59.253034
335	UREIA -------------- 20% ACIDO SALICILICO -------------- 4% LACTATO DE AMONIO -------------- 12% CREME HIDRATANTE -------------- 250 G	\N	topical	\N	aplicar nos braços 1x/dia À noite	2026-03-03 14:14:18.772215
336	AGE PROTEON EYE	\N	topical	\N	APLICAR NAS AREAS DOS OLHOS 1-2X/DIA	2026-03-04 12:26:50.539606
337	Creme Anti-Idade Profuse Densifiant Fondant	\N	topical	\N	aplicar no rosto À noite e retirar pela manhã	2026-03-04 17:58:08.968041
338	Creme Noturno Healthy Renew	\N	topical	\N	aplicar no rosto À noite e retirar pela manhã	2026-03-04 17:59:52.58873
339	HYALU B5 CREME SUPERATIVADO	\N	topical	\N	aplicar no rosto À noite e retirar pela manhã	2026-03-09 12:21:32.756645
340	PIELLUS FORTE	\N	topical	\N	LAVAR O COURO CABELUDO 1X/DIA	2026-03-09 14:13:09.734899
341	KELUAL SQUANORM  Kelual S Shampoo anticaspa DUCRAY	\N	topical	\N	LAVAR O COURO CABELUDO 1X/DIA	2026-03-09 14:14:20.03218
342	KELUAL SQUANORM Kelual S Shampoo anticaspa DUCRAY	\N	topical	\N	LAVAR O COURO CABELUDO 1X/DIA	2026-03-09 14:14:23.506394
343	terbinafina 250mg	\N	oral	\N	tomar 1 cp vo por dia por 3 meses	2026-03-10 18:52:08.024529
344	ISDIN Protetor Solar Facial em bastão Invisible Stick FPS 50-	\N	topical	\N	aplicar no rosto 2x/dia	2026-03-10 19:09:49.057836
\.


--
-- Data for Name: message_read; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.message_read (id, message_id, user_id, read_at) FROM stdin;
1	1	4	2025-12-05 17:48:08.793043
2	2	5	2025-12-09 19:27:53.643172
3	3	4	2025-12-09 20:28:30.661291
4	4	5	2025-12-09 20:30:41.282637
5	5	5	2025-12-09 20:55:48.205943
6	6	4	2025-12-11 17:05:07.456012
7	7	4	2026-02-11 18:39:48.499038
8	8	4	2026-02-27 18:18:51.144569
9	10	4	2026-02-27 20:12:43.16986
10	9	4	2026-02-27 20:12:43.169891
11	11	4	2026-03-02 11:39:15.498642
12	12	4	2026-03-02 11:39:15.49868
13	13	4	2026-03-02 11:40:04.04459
14	14	4	2026-03-02 11:40:04.044655
15	15	5	2026-03-02 11:40:28.051394
16	20	4	2026-03-02 12:32:57.070395
17	17	4	2026-03-02 12:32:57.070424
18	18	4	2026-03-02 12:32:57.070432
19	21	4	2026-03-02 12:32:57.070439
20	19	4	2026-03-02 12:32:57.070449
21	16	4	2026-03-02 12:32:57.070456
22	23	4	2026-03-02 12:58:14.135633
23	22	4	2026-03-02 12:58:14.13566
24	25	4	2026-03-02 14:00:44.820784
25	26	4	2026-03-02 14:00:44.820813
26	24	4	2026-03-02 14:00:44.820827
27	27	4	2026-03-02 14:03:01.511195
28	28	4	2026-03-02 20:39:17.638031
29	29	5	2026-03-02 20:40:44.525789
30	30	4	2026-03-11 11:04:49.054612
31	31	5	2026-03-11 17:49:45.829604
32	32	4	2026-03-11 17:50:44.263937
33	33	5	2026-03-11 17:55:00.168666
34	34	5	2026-03-11 17:55:00.168695
35	38	12	2026-03-11 18:17:44.382342
36	40	4	2026-03-11 18:35:53.523427
37	35	4	2026-03-11 18:35:53.523543
38	41	5	2026-03-11 18:38:27.85219
39	37	10	2026-03-11 19:09:40.851722
\.


--
-- Data for Name: note; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.note (id, patient_id, doctor_id, appointment_id, note_type, category, content, consultation_duration, created_at, transplant_indication, surgical_planning) FROM stdin;
1	2	5	2	queixa	cosmiatria	rugas na face	\N	2025-11-25 18:52:40.48672	nao	\N
2	2	5	2	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-11-25 18:52:40.539561	nao	\N
3	2	5	2	conduta	cosmiatria	[Conduta registrada via procedimentos]	20	2025-11-25 18:52:40.583776	nao	\N
8	1	5	13	queixa	cosmiatria	Rugas na face	\N	2025-11-27 23:02:33.840791	nao	\N
9	1	5	13	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-11-27 23:02:33.946047	nao	\N
10	1	5	13	conduta	cosmiatria	[Conduta registrada via procedimentos]	1	2025-11-27 23:02:33.98983	nao	\N
29	25	5	32	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-02 19:30:47.159338	nao	\N
13	17	5	22	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-11-28 19:52:12.234685	nao	\N
14	17	5	22	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2025-11-28 19:52:12.285457	nao	\N
17	18	5	25	queixa	cosmiatria	manchas na pele	\N	2025-12-02 12:51:14.941386	nao	\N
18	18	5	25	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.\n\n\nmelanose solar e lentigo solar na face\ndermatofibroma no joelho	\N	2025-12-02 12:51:14.98857	nao	\N
19	18	5	25	diagnostico	cosmiatria	lentigo solar \ndermatofibroma	\N	2025-12-02 12:51:15.031918	nao	\N
20	18	5	25	conduta	cosmiatria	Uso Tópico\ncetaphil percting serum anti manchas\nAPLICAR NO ROSTO à NOITE E RETIRAR PELA MANHÃ\nHYDROBOOST GEL DE LIMPEZA NEUTROGENA\nLAVAR O ROSTO 2X/DIA POR DIA\nEpisol Color FPS 70\nAPLICAR NO ROSTO 1-2X/DIA	2	2025-12-02 12:51:15.075648	nao	\N
21	19	5	26	queixa	cosmiatria	quer fazer btoox	\N	2025-12-02 13:03:31.792156	nao	\N
22	19	5	26	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-02 13:03:31.839865	nao	\N
23	19	5	26	conduta	cosmiatria	[Conduta registrada via procedimentos]	4	2025-12-02 13:03:31.883605	nao	\N
24	20	5	27	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2025-12-02 13:21:53.149033	nao	\N
25	20	5	27	anamnese	transplante_capilar	area doadora muito ruim\n barba e peito bom	\N	2025-12-02 13:21:53.19845	nao	\N
26	20	5	27	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	14	2025-12-02 13:21:53.242842	nao	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": true, "eyebrow_transplant": false, "beard_transplant": false, "frontal": false, "crown": false, "complete": false, "complete_body_hair": false, "surgical_planning_text": "calvicie muito extensa\\narea doadora ruim\\npenso em 2500 capilar \\n1000 barba e 2000 peito\\n\\nainda sim ficara ralo com desenho conservador"}
27	21	5	28	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-02 14:01:24.493749	nao	\N
28	21	5	28	conduta	cosmiatria	advatan\naplicar nas lesoes 1x/dia por 5 dias\nCreme Facial Diário Fisiogel A.I.\nAPLICAR NO ROSTO 2-3X/DIA\nEPIDRAT CALM\nAPLICAR NO ROSTO 3-4X/DIA	0	2025-12-02 14:01:24.544548	nao	\N
30	25	5	32	conduta	cosmiatria	na verdade hj fez retoque botox	0	2025-12-02 19:30:47.214998	nao	\N
31	33	5	44	queixa	cosmiatria	nodulo na face	\N	2025-12-03 18:47:43.433878	nao	\N
32	33	5	44	anamnese	cosmiatria	ultrassom  fala a favor de granuloma\n\nnao indetifica se é biosestimulador ou acido hialuronico\n\nnodulo na regiao malar visivel e palpavel	\N	2025-12-03 18:47:43.491316	nao	\N
33	33	5	44	diagnostico	cosmiatria	granuloma	\N	2025-12-03 18:47:43.534679	nao	\N
34	33	5	44	conduta	cosmiatria	[Conduta registrada via procedimentos]	2	2025-12-03 18:47:43.577654	nao	\N
35	30	5	39	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2025-12-03 20:06:05.782391	nao	\N
36	30	5	39	conduta	transplante_capilar	calvicie grande coroa principal\nindco 50 frontal\ne 50 coroa\nfios finos\ndeixei claro q a coroa é insuficiente\nfazer hairline conservadora	3	2025-12-03 20:06:05.831005	sim	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "frontal": false, "crown": false, "complete": false, "complete_body_hair": false, "surgical_planning_text": ""}
37	28	5	36	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2025-12-03 20:10:52.036665	nao	\N
38	28	5	36	conduta	transplante_capilar	transplnate coroa	1	2025-12-03 20:10:52.077724	sim	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "frontal": false, "crown": true, "complete": false, "complete_body_hair": false, "surgical_planning_text": "apenas coroa sem fazer frontal"}
39	34	5	45	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-04 17:16:19.285581	nao	\N
40	34	5	45	conduta	cosmiatria	[Conduta registrada via procedimentos]	1	2025-12-04 17:16:19.381861	nao	\N
41	35	5	46	queixa	patologia	estrias nas pernas\n verrugas curadas	\N	2025-12-04 20:41:41.69196	nao	\N
42	35	5	46	anamnese	patologia	estrias vermelhas interno de coxa e coxa	\N	2025-12-04 20:41:41.788993	nao	\N
43	35	5	46	conduta	patologia	striactive e vitanl 0,5	0	2025-12-04 20:41:41.834515	nao	\N
4	11	5	23	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2025-11-27 18:06:51.123293	nao	\N
44	38	5	51	queixa	transplante_capilar	ja fez um trnasplante ha 1 ano	\N	2025-12-05 13:24:08.558575	nao	\N
45	38	5	51	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	1	2025-12-05 13:24:08.610794	sim	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "frontal": false, "crown": false, "complete": true, "complete_body_hair": false, "surgical_planning_text": "cabelo branco fios finos"}
46	37	5	50	queixa	cosmiatria	fez botox ha 1 mes	\N	2025-12-05 13:27:29.404719	nao	\N
47	37	5	50	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-05 13:27:29.450771	nao	\N
48	37	5	50	conduta	cosmiatria	reveline retinol\nefaclar concetrado\nfps	0	2025-12-05 13:27:29.497903	nao	\N
49	36	5	49	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-05 13:28:35.35775	nao	\N
50	36	5	49	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2025-12-05 13:28:35.400375	nao	\N
51	39	5	52	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2025-12-05 13:39:08.658091	nao	\N
52	39	5	52	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	9	2025-12-05 13:39:08.700393	sim	{"norwood": null, "previous_transplant": "sim", "transplant_location": "outro_servico", "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "frontal": false, "crown": true, "complete": true, "complete_body_hair": false, "surgical_planning_text": ""}
53	47	5	61	queixa	cosmiatria	ja faz botox	\N	2025-12-09 18:10:25.290517	nao	\N
54	47	5	61	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-09 18:10:25.386097	nao	\N
55	47	5	61	conduta	cosmiatria	[Conduta registrada via procedimentos]	8	2025-12-09 18:10:25.43105	nao	\N
56	46	5	60	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-09 18:17:20.954175	nao	\N
57	46	5	60	conduta	cosmiatria	[Conduta registrada via procedimentos]	4	2025-12-09 18:17:21.00143	nao	\N
58	49	5	64	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-09 19:09:48.529208	nao	\N
59	49	5	64	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2025-12-09 19:09:48.574935	nao	\N
60	48	5	62	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-09 19:16:08.135332	nao	\N
61	48	5	62	conduta	cosmiatria	fez 2 aplicaoes de infltracao capilar fechou pacote com 4 \n\nhj ja esta cheio de cabelinhos	6	2025-12-09 19:16:08.181955	nao	\N
62	42	5	56	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2025-12-09 20:31:48.775923	nao	\N
63	42	5	56	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	0	2025-12-09 20:31:48.823201	sim	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "frontal": true, "crown": false, "complete": false, "complete_body_hair": false, "surgical_planning_text": "dense packing um pouco de escalpe medio\\narea  doadora  muito boa"}
64	44	5	58	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2025-12-09 20:33:49.898771	nao	\N
65	44	5	58	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	0	2025-12-09 20:33:49.93948	sim	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "frontal": true, "crown": false, "complete": false, "complete_body_hair": false, "surgical_planning_text": "frontal manter a hairline"}
66	43	5	57	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-09 20:34:20.811639	nao	\N
67	43	5	57	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2025-12-09 20:34:20.85117	nao	\N
68	41	5	55	anamnese	cosmiatria	sulco papada\npalpebras	\N	2025-12-09 20:53:49.306929	nao	\N
69	41	5	55	diagnostico	cosmiatria	estetica	\N	2025-12-09 20:53:49.346246	nao	\N
70	41	5	55	conduta	cosmiatria	[Conduta registrada via procedimentos]	18	2025-12-09 20:53:49.385353	nao	\N
71	50	5	65	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-10 17:52:32.585643	nao	\N
72	50	5	65	conduta	cosmiatria	[Conduta registrada via procedimentos]	1	2025-12-10 17:52:32.683916	nao	\N
73	51	5	66	anamnese	patologia	afinamento do cabelo em uso de megahair\ntem baby hair na hairline	\N	2025-12-10 18:05:05.554438	nao	\N
74	51	5	66	conduta	patologia	NEOSIL ATTACK\nTOMAR 1 CP VO POR DIA POR 3 MESES\nMINOXIDIL 1MG (USO CONTINUO)\nTOMAR 1 CP VO POR DIA	0	2025-12-10 18:05:05.60138	nao	\N
75	52	5	67	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2025-12-10 18:37:06.459803	nao	\N
117	81	5	97	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-12 19:56:09.192791	nao	\N
118	81	5	97	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2025-12-12 19:56:09.243968	nao	\N
119	75	5	90	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2025-12-12 20:14:29.295156	nao	\N
158	100	5	122	conduta	cosmiatria	melanose solar e lentigo solar quer tirar\n\ntalvez limeght\n\npasso dual serum e fusion water	0	2026-01-19 18:55:09.458584	nao	\N
76	52	5	67	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	2	2025-12-10 18:37:06.504917	sim	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "frontal": true, "crown": true, "complete": false, "complete_body_hair": false, "surgical_planning_text": "corora e dense packing"}
77	57	5	72	queixa	transplante_capilar	alvicie feminina\nrarefacao homogenea\n.	\N	2025-12-10 19:15:38.57645	nao	\N
78	57	5	72	anamnese	transplante_capilar	area doadora muito ruim fio muito fino	\N	2025-12-10 19:15:38.62716	nao	\N
79	57	5	72	diagnostico	transplante_capilar	alopecia androgenetica feminina	\N	2025-12-10 19:15:38.671392	nao	\N
80	57	5	72	conduta	transplante_capilar	fazer o transpalnte na menor area possivel\n areadoadora ruim\nmuito fino ralo pensei 2000-2500	2	2025-12-10 19:15:38.715743	sim	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "frontal": false, "crown": false, "complete": false, "complete_body_hair": false, "surgical_planning_text": "fazer o transpalnte na menor area possivel\\n areadoadora ruim\\nmuito fino ralo pensei 2000-2500"}
81	54	5	69	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-11 12:04:07.741535	nao	\N
82	54	5	69	conduta	cosmiatria	1 renova labios 0,8 labios e 0,4 nariz 1 voluma c1 0,6 e 0,4 sulco	0	2025-12-11 12:04:07.803475	nao	\N
83	58	5	73	queixa	patologia	lipedema	\N	2025-12-11 12:34:25.997516	nao	\N
84	58	5	73	anamnese	patologia	edema e espessamento dos mmmii	\N	2025-12-11 12:34:26.040642	nao	\N
85	58	5	73	diagnostico	patologia	lipedema	\N	2025-12-11 12:34:26.083679	nao	\N
86	58	5	73	conduta	patologia	orientacoa exercicio fisico	0	2025-12-11 12:34:26.12685	nao	\N
87	59	5	74	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-11 12:35:39.230609	nao	\N
88	59	5	74	conduta	cosmiatria	botox 30u	0	2025-12-11 12:35:39.27656	nao	\N
89	60	5	75	queixa	patologia	MELASMA	\N	2025-12-11 14:55:22.488489	nao	\N
90	60	5	75	anamnese	patologia	HIPERCERATOSE FOLICULAR GLUTEO\nMELASMA	\N	2025-12-11 14:55:22.53614	nao	\N
91	60	5	75	conduta	patologia	herapsor solucao\naplicar 8 -10 gotas na regiao afetada 1 x/dia por 5 dias reutilizar se necessa´rio\nEPIDRAT CALM\nAPLICAR NO ROSTO 3-4X/DIA\nAnti-Pigment Dual Sérum\naplicar no rosto À noite e retirar pela manhã\ncleanance gel\nLAVAR O ROSTO 2X/DIA\nAnti-Pigment Creme Corporal para Áreas Específicas\nAplicar uma fina camada nas áreas com manchas 1-2 vezes ao dia	1	2025-12-11 14:55:22.581083	nao	\N
92	61	5	76	anamnese	cosmiatria	CALVICIE FEMININA JA FEZ TRANSPLANTE CAPILAR EM OUTRO SERVICO	\N	2025-12-11 14:56:47.863429	nao	\N
93	61	5	76	diagnostico	cosmiatria	ALOPECIA ANDROGENETICA FEMINA	\N	2025-12-11 14:56:47.907852	nao	\N
94	61	5	76	conduta	cosmiatria	FEZ HJ INFILTRACAO CAPILAR	1	2025-12-11 14:56:47.951843	nao	\N
95	62	5	77	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-11 15:16:38.633032	nao	\N
96	62	5	77	conduta	cosmiatria	FEZ MORPHEUS FACE EM AGOSTO DE 25	1	2025-12-11 15:16:38.679812	nao	\N
97	63	5	78	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-11 17:59:53.62103	nao	\N
98	63	5	78	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2025-12-11 17:59:53.66685	nao	\N
99	64	5	79	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-11 18:33:22.895853	nao	\N
100	64	5	79	conduta	cosmiatria	[Conduta registrada via procedimentos]	10	2025-12-11 18:33:22.94082	nao	\N
101	65	5	80	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-11 19:19:02.858929	nao	\N
102	65	5	80	conduta	cosmiatria	[Conduta registrada via procedimentos]	10	2025-12-11 19:19:02.903593	nao	\N
103	67	5	82	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-12 12:41:57.442136	nao	\N
104	67	5	82	conduta	cosmiatria	[Conduta registrada via procedimentos]	2	2025-12-12 12:41:57.492912	nao	\N
105	70	5	85	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-12 12:57:43.765614	nao	\N
106	70	5	85	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2025-12-12 12:57:43.810696	nao	\N
107	66	5	81	anamnese	patologia	prurigo no corpo todo e rosacea\n\ntrattou com limecilina 12/12 sem melhora da rosacea\nacho q tem aver com o barbear	\N	2025-12-12 13:36:38.45609	nao	\N
108	66	5	81	conduta	patologia	Uso Tópico\nSUNFRESH OIL CONTROL FPS80 NEUTROGENA\nAPLICAR NO ROSTO 2X/DIA\nsuavie sabonete liquido\nlavar o rosto 2x/dia\nEPIDRAT CALM\nAPLICAR NO ROSTO 3-4X/DIA\n\n\ndoxaciclina 100mg\n\nTomar 1cp vo de 12/12h por 30 dias\n\nUso Tópico\n\n1.\nrozex\n\nAplicar no rosto à noite e retirar pela manhã	0	2025-12-12 13:36:38.510894	nao	\N
109	74	5	89	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-12 14:08:04.153637	nao	\N
110	74	5	89	conduta	cosmiatria	etirp no queixo deixo corticoide caso precise	0	2025-12-12 14:08:04.199047	nao	\N
111	72	5	87	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-12 17:36:36.638024	nao	\N
112	72	5	87	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2025-12-12 17:36:36.683084	nao	\N
113	77	5	92	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-12 18:56:35.266465	nao	\N
114	77	5	92	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2025-12-12 18:56:35.311718	nao	\N
115	78	5	96	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-12 18:56:58.13118	nao	\N
116	78	5	96	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2025-12-12 18:56:58.1762	nao	\N
120	75	5	90	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	1	2025-12-12 20:14:29.339914	sim	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": true, "crown": false, "complete": false, "complete_body_hair": false, "dense_packing": true, "surgical_planning_text": ""}
121	1	5	98	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-12 20:17:35.267312	nao	\N
122	1	5	98	conduta	cosmiatria	[Conduta registrada via procedimentos]	1	2025-12-12 20:17:35.312647	nao	\N
123	83	5	100	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-15 13:18:40.015079	nao	\N
124	83	5	100	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2025-12-15 13:18:40.066222	nao	\N
125	84	5	101	queixa	patologia	mancha na pele	\N	2025-12-15 13:20:47.04434	nao	\N
126	84	5	101	anamnese	patologia	2 nevos na regiao da costeleta	\N	2025-12-15 13:20:47.089584	nao	\N
127	84	5	101	diagnostico	patologia	lentigo solar e qs	\N	2025-12-15 13:20:47.135449	nao	\N
128	84	5	101	conduta	patologia	orientacao	0	2025-12-15 13:20:47.180957	nao	\N
129	85	5	102	queixa	cosmiatria	deramtofibroma	\N	2025-12-15 13:35:58.172237	nao	\N
130	85	5	102	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-15 13:35:58.215712	nao	\N
131	85	5	102	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2025-12-15 13:35:58.257675	nao	\N
132	85	5	102	queixa	cosmiatria	dermatofibroma	\N	2025-12-15 13:42:15.306427	nao	\N
133	85	5	102	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-15 13:42:15.351111	nao	\N
134	85	5	102	conduta	cosmiatria	[Conduta registrada via procedimentos]	12	2025-12-15 13:42:15.394923	nao	\N
135	80	5	104	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2025-12-15 13:43:14.76441	nao	\N
136	80	5	104	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	0	2025-12-15 13:43:14.809123	sim	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": false, "crown": false, "complete": true, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": ""}
137	82	5	99	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-15 14:21:11.292999	nao	\N
138	82	5	99	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2025-12-15 14:21:11.337112	nao	\N
139	89	5	107	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2025-12-15 18:34:51.02521	nao	\N
140	89	5	107	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	0	2025-12-15 18:34:51.068388	sim	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": false, "crown": false, "complete": true, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": ""}
141	86	5	103	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-15 18:58:15.119922	nao	\N
142	86	5	103	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2025-12-15 18:58:15.165684	nao	\N
143	92	5	110	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-15 20:03:59.681681	nao	\N
144	92	5	110	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2025-12-15 20:03:59.727028	nao	\N
145	94	5	112	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-16 14:00:57.851559	nao	\N
146	94	5	112	conduta	cosmiatria	[Conduta registrada via procedimentos]	1	2025-12-16 14:00:57.904437	nao	\N
147	95	5	113	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-16 18:32:44.914555	nao	\N
148	95	5	113	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2025-12-16 18:32:44.961015	nao	\N
149	48	5	115	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2025-12-17 14:07:04.290879	nao	\N
150	48	5	115	conduta	cosmiatria	[Conduta registrada via procedimentos]	1	2025-12-17 14:07:04.343033	nao	\N
151	98	5	119	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-01-19 17:26:46.410419	nao	\N
152	98	5	119	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-01-19 17:26:46.458918	nao	\N
153	54	5	120	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-01-19 17:41:18.97312	nao	\N
154	54	5	120	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-01-19 17:41:19.014039	nao	\N
155	99	5	121	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-01-19 18:54:20.150688	nao	\N
156	99	5	121	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-01-19 18:54:20.200729	nao	\N
157	100	5	122	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-01-19 18:55:09.414871	nao	\N
361	281	5	324	queixa	patologia	papulas foliculares	\N	2026-02-26 13:33:29.945009	nao	\N
159	63	5	118	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-01-19 19:40:36.866795	nao	\N
160	63	5	118	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-01-19 19:40:36.912855	nao	\N
161	104	5	128	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-01-21 14:47:13.370608	nao	\N
162	104	5	128	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-01-21 14:47:13.420669	nao	\N
163	101	5	124	conduta	patologia	sunfresh e orientação geral	0	2026-01-21 17:56:48.571432	nao	\N
164	102	5	125	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-01-21 17:59:10.344064	nao	\N
165	102	5	125	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	1	2026-01-21 17:59:10.389711	sim	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": true, "crown": false, "complete": false, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": "foco total na frente escalpe e coroa pode segurar com medicamento"}
166	103	5	126	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-01-21 18:04:37.083335	nao	\N
167	103	5	126	conduta	cosmiatria	paciente tem rosacea intesa ela é toda vermelha tem telagectasia fez laser em franca mas fala q nao melhorou\npasso rosex  e fazer limelight em 3-4 m	5	2026-01-21 18:04:37.131663	nao	\N
168	105	5	129	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-01-21 18:30:00.317152	nao	\N
169	105	5	129	conduta	cosmiatria	Paciente: LUCIANA FINOTO MELO\n\nUso Tópico\nderivamicro\nAPLICAR NO ROSTO à NOITE E RETIRAR PELA MANHÃ\nHyalu B5 Serum\nAPLICAR NO ROSTO à NOITE E RETIRAR PELA MANHÃ\nefaclar alta tolerancia\nlavar o rosto 2x/dia\nessencele c 20\nAPLICAR NO ROSTO PELA MANHA ANTES DO FPS	9	2026-01-21 18:30:00.363065	nao	\N
170	107	5	132	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-01-21 19:27:47.660584	nao	\N
171	107	5	132	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	25	2026-01-21 19:27:47.706253	sim	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": true, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": false, "crown": false, "complete": true, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": "CALVICIE EXTENSA DESENHO CONSERVADOR MANTER A HAIRLINE E A ENTRADA"}
172	96	5	130	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-01-21 20:16:32.56496	nao	\N
173	96	5	130	conduta	cosmiatria	[Conduta registrada via procedimentos]	29	2026-01-21 20:16:32.608382	nao	\N
174	108	5	133	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-01-21 20:22:19.487998	nao	\N
175	108	5	133	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	2	2026-01-21 20:22:19.532373	sim	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": true, "crown": false, "complete": true, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": "MELHORA DA HAIRLINE"}
176	109	5	134	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-01-21 20:23:13.777185	nao	\N
177	109	5	134	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-01-21 20:23:13.822172	nao	\N
178	111	5	136	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-01-21 20:24:43.031254	nao	\N
179	111	5	136	conduta	cosmiatria	[Conduta registrada via procedimentos]	1	2026-01-21 20:24:43.075819	nao	\N
180	114	5	139	diagnostico	patologia	queimadura solar na face	\N	2026-01-22 13:39:54.01412	nao	\N
181	114	5	139	conduta	patologia	nevo ok\n apenas orientacao	0	2026-01-22 13:39:54.134544	nao	\N
182	113	5	138	conduta	patologia	retinol b3 serum\ncerave olhos\n\nindico cirurgiao plasstico para tirar nevos pq marido é medico da unimed	0	2026-01-22 13:40:34.703613	nao	\N
183	115	5	140	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-01-22 13:41:59.977609	nao	\N
184	115	5	140	diagnostico	cosmiatria	acne da mulher adulta	\N	2026-01-22 13:42:00.021282	nao	\N
185	115	5	140	conduta	cosmiatria	ja usou limeciclina 4 meses e zella\ncom otimo resultado\npara acne indico pacte peeling para melasma\ne introduzo vitacidplus tambem	1	2026-01-22 13:42:00.064276	nao	\N
186	116	5	141	queixa	patologia	quedad de cabelo pos face\ndermatofibroma na coxa\nnevo rubi no seio	\N	2026-01-22 14:14:20.506188	nao	\N
187	116	5	141	conduta	patologia	NOURKRIN\nTOMAR 1 CP VO PELA MANHÃ E 1 CP VO à NOITE POR 3 MESES\ncollagen h.a mantecorp\ntomar 1 sachet por dia por 3 meses\nUso Tópico\nRetinol B3 Serum\nAPLICAR NO ROSTO à NOITE E RETIRAR PELA MANHÃ\nessencele c 20\nAPLICAR NO ROSTO PELA MANHA ANTES DO FPS\nk-ox eye\naplicar nas areas dos olhos 2x/dia\n\nvitacidplus e eucerin corpoarl para mancha pos subcisao no gluteo	0	2026-01-22 14:14:20.549337	nao	\N
188	97	5	142	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-01-22 14:22:46.798984	nao	\N
189	97	5	142	conduta	cosmiatria	[Conduta registrada via procedimentos]	7	2026-01-22 14:22:46.843102	nao	\N
190	122	5	148	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-01-23 19:21:02.575361	nao	\N
191	122	5	148	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-01-23 19:21:02.627973	nao	\N
192	120	5	146	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-01-23 19:22:54.304954	nao	\N
193	120	5	146	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	1	2026-01-23 19:22:54.351347	nao	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": false, "crown": false, "complete": false, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": ""}
194	121	5	147	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-01-23 20:04:22.782398	nao	\N
195	121	5	147	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-01-23 20:04:22.826437	nao	\N
196	123	5	149	queixa	patologia	espihjas ja usou epiduo agora troquei por clindoxyul	\N	2026-01-23 20:05:13.809169	nao	\N
197	123	5	149	conduta	patologia	melhora parcial em um de progesterona como aco\n\ninicio espiro 200\nhyalu b5 water gel	0	2026-01-23 20:05:13.855208	nao	\N
198	124	5	150	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-01-26 18:18:55.611511	nao	\N
199	124	5	150	diagnostico	cosmiatria	NEVO MELANOCITICO	\N	2026-01-26 18:18:55.666553	nao	\N
200	124	5	150	conduta	cosmiatria	FAÇO HJ EXERESE DE LESAO NA FACE NEVO MELANOCITICO	1	2026-01-26 18:18:55.719654	nao	\N
201	126	5	152	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-01-26 18:52:15.489735	nao	\N
202	126	5	152	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	4	2026-01-26 18:52:15.537683	sim	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": false, "crown": false, "complete": true, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": "cabelo fino\\ntem indica\\u00e7ao de um anova ciruirgia"}
203	128	5	154	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-01-26 19:51:07.439037	nao	\N
204	128	5	154	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-01-26 19:51:07.48463	nao	\N
205	130	5	156	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-01-26 20:12:56.551577	nao	\N
206	130	5	156	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-01-26 20:12:56.596118	nao	\N
207	131	5	158	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-01-27 12:57:33.639542	nao	\N
208	131	5	158	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\nFAZER 70 COROA E 30 FRONTAL SO ENTRADINHA  OU 60 40	34	2026-01-27 12:57:33.762778	sim	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": false, "crown": false, "complete": true, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": "PACIENTE TEM PRIORIDADE COROA"}
209	74	5	157	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-01-27 14:28:34.936089	nao	\N
210	74	5	157	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-01-27 14:28:34.981513	nao	\N
211	132	5	159	queixa	patologia	hiperceratose folicular nos bracos e pernas	\N	2026-01-27 14:29:26.076645	nao	\N
212	132	5	159	conduta	patologia	formula	0	2026-01-27 14:29:26.121815	nao	\N
219	134	5	161	queixa	patologia	queda de cabelo	\N	2026-01-27 14:31:28.69066	nao	\N
220	134	5	161	conduta	patologia	Uso Oral\nNEOSIL ATTACK\nTOMAR 1 CP VO POR DIA POR 3 MESES\nUso Tópico\nAnti-Pigment Dual Sérum\naplicar no rosto À noite e retirar pela manhã\nessencele c 20\nAPLICAR NO ROSTO PELA MANHA ANTES DO FPS\nivy c corpo\naplicar no colo 1-2x/dia	0	2026-01-27 14:31:28.735399	nao	\N
221	133	5	160	queixa	patologia	paciente veio ha 1 mes com foliclute ecorida nas costas tipo um eczema folicular\ntratei com diporspan e halobex e atoderm com melhora completa poem hj teve uma erupcao acneiforme nas costas e voltou um pouco as lesoes  mas bem mais brandas q da outra vez	\N	2026-01-27 14:33:11.537123	nao	\N
222	133	5	160	conduta	patologia	melhora parcial\n foi totalnos primeiros dias mas ainda tem lesoe sbem foliculares\ninicio limecilina ate pq alem de ser um foliculitre teve uma erupcao acneiforme	1	2026-01-27 14:33:11.583646	nao	\N
223	136	5	163	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-01-27 14:34:29.405329	nao	\N
224	136	5	163	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-01-27 14:34:29.450114	nao	\N
225	137	5	164	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-01-27 14:35:12.163326	nao	\N
234	141	5	168	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-01-27 19:10:30.495268	nao	\N
235	141	5	168	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	1	2026-01-27 19:10:30.541979	sim	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": false, "crown": false, "complete": true, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": "60 frontal e 10 escalpe e 30 coroa\\napesar de ter preferencia na coroa"}
236	144	5	171	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-01-27 20:13:20.750735	nao	\N
237	144	5	171	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\nininciar tratamento depois	0	2026-01-27 20:13:20.796618	sim	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": true, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": false, "crown": false, "complete": false, "complete_body_hair": true, "dense_packing": false, "surgical_planning_text": "calvicie extensa\\narea doadora pequena\\nindico body hair ocm desenho bem conservador imaginei 2500 a 3 capilar e 2000 barba e pelo"}
240	149	5	176	conduta	patologia	nl\n verrugas no pe	0	2026-02-02 14:14:07.707393	nao	\N
255	118	5	188	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-02-03 13:06:16.849615	nao	\N
256	118	5	188	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\ntiro foto 03/2/26	2	2026-02-03 13:06:16.89888	nao	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": false, "crown": false, "complete": false, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": ""}
261	169	5	198	queixa	patologia	QS E\nCOCEIRA NO CORPO	\N	2026-02-03 14:32:34.03007	nao	\N
262	169	5	198	conduta	patologia	CETAPHIL E HIXIZINE	0	2026-02-03 14:32:34.074683	nao	\N
263	162	5	190	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-03 17:27:59.896736	nao	\N
264	162	5	190	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-02-03 17:27:59.942125	nao	\N
265	106	5	191	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-02-03 18:16:43.173433	nao	\N
266	106	5	191	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	1	2026-02-03 18:16:43.217903	sim	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": false, "crown": true, "complete": false, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": ""}
267	170	5	199	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-03 20:04:17.142274	nao	\N
268	170	5	199	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-02-03 20:04:17.187794	nao	\N
269	171	5	200	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-02-04 12:59:51.27758	nao	\N
233	140	5	167	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-01-27 18:35:09.047672	nao	\N
270	171	5	200	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n🧾 PRESCRIÇÃO MÉDICA\n\nPaciente: ALEXANDRE VINICIUS DA SILVA PEREIRA\n\n💊 Uso Oral:\n- NEOSIL ATTACK\n  TOMAR 01 CP VO POR DIA POR 3 MESES\n- MINOXIDIL 2,5MG\n  TOMAR 01 CP VO POR DIA\n\n🧴 Uso Tópico:\n- CAPPY\n  APLICAR NO COURO CABELUDO 1X/DIA\n\nDr. Arthur Basile – CRM 125.217\nDermatologista\n\nClínica Basile – Av. Prof. João Fiúsa, 2300 – Ribeirão Preto – SP\nwww.clinicabasile.com.br | Fone/Fax: (16) 3602-7785	17	2026-02-04 12:59:51.327448	nao	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": false, "crown": false, "complete": false, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": ""}
273	173	5	202	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-04 17:32:21.391744	nao	\N
274	173	5	202	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-02-04 17:32:21.436349	nao	\N
275	175	5	204	queixa	cosmiatria	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-02-04 19:08:38.822835	nao	\N
276	175	5	204	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-04 19:08:38.869118	nao	\N
277	175	5	204	conduta	cosmiatria	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	0	2026-02-04 19:08:38.915182	nao	\N
278	177	5	206	queixa	cosmiatria	NEVO NA FACE	\N	2026-02-05 13:03:12.243897	nao	\N
279	177	5	206	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-05 13:03:12.293126	nao	\N
280	177	5	206	conduta	cosmiatria	[Conduta registrada via procedimentos]	1	2026-02-05 13:03:12.337773	nao	\N
290	184	5	213	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-02-05 19:28:18.323366	nao	\N
291	184	5	213	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	7	2026-02-05 19:28:18.367472	nao	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": false, "crown": false, "complete": false, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": ""}
292	188	5	217	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-05 19:34:58.047245	nao	\N
293	188	5	217	conduta	cosmiatria	[Conduta registrada via procedimentos]	2	2026-02-05 19:34:58.08983	nao	\N
294	187	5	216	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-02-05 20:50:46.527271	nao	\N
362	281	5	324	conduta	patologia	boa melhora\ntinha acne no doroso pos diprospan\n hj praticamente sem anda\n mantive o antibiotico mais 15 dias 12/12\nacho q tem estrese evnolvido parou muito no carnaval\n\nse nao melhorar pensei em biopsia pra excluir liquen plano pilar	0	2026-02-26 13:33:30.052892	nao	\N
365	299	5	343	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-27 18:31:44.964019	nao	\N
366	299	5	343	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-02-27 18:31:45.005732	nao	\N
367	296	5	340	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-02-27 18:32:58.102368	nao	\N
260	161	5	189	conduta	patologia	zella\naplicar no rosto À noite e retirar pela manhã\natoderm baume 500ml\naplicar no corpo 2x/dia\natoderm gel creme\nAPLICAR NO CORPO 3-4X/DIA\nAnti-Pigment Creme Corporal para Áreas Específicas\nAplicar uma fina camada nas áreas com manchas 1-2 vezes ao dia	0	2026-02-03 13:41:33.1251	nao	\N
295	187	5	216	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n🧾 PRESCRIÇÃO MÉDICA\n\nPaciente: DIOGO ARROYO\n\n💊 Uso Oral:\n- NEOSIL ATTACK\n  TOMAR 01 CP VO POR DIA POR 3 MESES\n- MINOXIDIL 2,5MG\n  TOMAR 01 CP VO POR DIA\n- FINASTERIDA 1MG\n  TOMAR 1 CP VO POR DIA\n\n🧴 Uso Tópico:\n- CAPPY\n  APLICAR NO COURO CABELUDO 1X/DIA\n\nDr. Arthur Basile – CRM 125.217\nDermatologista\n\nClínica Basile – Av. Prof. João Fiúsa, 2300 – Ribeirão Preto – SP\nwww.clinicabasile.com.br | Fone/Fax: (16) 3602-7785	1	2026-02-05 20:50:46.56934	sim	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": false, "crown": false, "complete": false, "complete_body_hair": false, "dense_packing": true, "surgical_planning_text": "PACIENTE MUITO  NOVO\\nTEM MUITA ENTRADQA MAS NAO TRATA"}
296	189	5	218	queixa	patologia	cisto sebaceo na face ha 3 meses	\N	2026-02-06 12:22:02.438953	nao	\N
297	189	5	218	diagnostico	patologia	cisto sebaceo	\N	2026-02-06 12:22:02.485175	nao	\N
298	189	5	218	conduta	patologia	oriento exerese da lesao\n1800 reais pcte tem unimed	5	2026-02-06 12:22:02.529217	nao	\N
299	225	5	257	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-11 13:57:29.563958	nao	\N
300	225	5	257	conduta	cosmiatria	zella\naplicar no rosto À noite e retirar pela manhã\nAnti-Pigment Dual Sérum\naplicar no rosto À noite e retirar pela manhã\nefaclar alta tolerancia\nlavar o rosto 2x/dia\nessencele c 20\nAPLICAR NO ROSTO PELA MANHA ANTES DO FPS	5	2026-02-11 13:57:29.618561	nao	\N
301	216	5	248	queixa	patologia	NEVO CONGENITO NA ORELHA ESQUERDA	\N	2026-02-11 14:11:18.79735	nao	\N
302	216	5	248	conduta	patologia	DERMATOSCOPIA OK SEM ALETRACOES NEVO INVADE O CONDUTO	0	2026-02-11 14:11:18.842389	nao	\N
303	217	5	249	conduta	patologia	NL	4	2026-02-11 14:18:59.057534	nao	\N
304	226	5	258	queixa	patologia	PV ZILERI POSITIVO	\N	2026-02-11 14:34:08.812824	nao	\N
305	226	5	258	conduta	patologia	cetoconazol 200mg\ntomar 1 cp vo por dia por 15 dias\nUso Tópico\nicaden spray\naplicar no corpo 2x/dia por 15 dias\natoderm gel creme\nAPLICAR NO CORPO 3-4X/DIA	0	2026-02-11 14:34:08.862349	nao	\N
306	218	5	250	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-11 17:49:46.856986	nao	\N
307	218	5	250	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-02-11 17:49:46.910754	nao	\N
308	219	5	251	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-11 18:11:35.205093	nao	\N
309	219	5	251	conduta	cosmiatria	[Conduta registrada via procedimentos]	1	2026-02-11 18:11:35.250931	nao	\N
310	220	5	252	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-11 18:58:21.490435	nao	\N
311	220	5	252	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-02-11 18:58:21.533496	nao	\N
312	223	5	255	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-02-11 20:14:34.075681	nao	\N
313	223	5	255	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\niniciar trataqmento depois parou ha 2 anos	0	2026-02-11 20:14:34.121055	sim	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": false, "crown": true, "complete": false, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": "na frente apenas detalhes 30%"}
314	228	5	260	queixa	cosmiatria	tem uma cicatr larga no nariz\n\ne cicatriz de acne\n\n\nindico cirurgia para cicatriz que é larga 2500\n\ne genesis  para cicatriz de acne\nUso Oral\nMINOXIDIL 1MG (USO CONTINUO)\nTOMAR 1 CP VO POR DIA\nUso Tópico\ncappy\nAPLICAR NO COURO CABELUDO 1X/DIA à NOITE	\N	2026-02-12 12:36:56.162274	nao	\N
315	228	5	260	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-12 12:36:56.21832	nao	\N
316	228	5	260	conduta	cosmiatria	tem uma cicatr larga no nariz\n\ne cicatriz de acne\n\n\nindico cirurgia para cicatriz que é larga 2500\n\ne genesis  para cicatriz de acne\nUso Oral\nMINOXIDIL 1MG (USO CONTINUO)\nTOMAR 1 CP VO POR DIA\nUso Tópico\ncappy\nAPLICAR NO COURO CABELUDO 1X/DIA à NOITE	0	2026-02-12 12:36:56.262059	nao	\N
317	227	5	259	queixa	patologia	nao teve melhora da foliculite ainda se queixa muito]\n\nmas nitidamente nao tem foliculite tem apenas  prurigo\n\npasso hixiinze 30 dias e therapsor 10 dias	\N	2026-02-12 13:09:50.338017	nao	\N
318	227	5	259	diagnostico	patologia	prurigo no couro cabeludo e no peito\nnao tem foliculite	\N	2026-02-12 13:09:50.383661	nao	\N
319	227	5	259	conduta	patologia	nao teve melhora da foliculite ainda se queixa muito]\n\nmas nitidamente nao tem foliculite tem apenas  prurigo\n\npasso hixiinze 30 dias e therapsor 10 dias\n\nse nao melhorar pensei em limecilinas	0	2026-02-12 13:09:50.429166	nao	\N
320	233	5	266	conduta	patologia	fez 2 transplante na coroa 2019 e 2020\nhj inico minoxidil oral e topico cabelo vem ficnado muito branco	0	2026-02-12 18:16:27.021941	nao	\N
321	232	5	265	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-12 18:37:21.392009	nao	\N
322	232	5	265	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-02-12 18:37:21.437946	nao	\N
323	239	5	272	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-13 13:29:30.406063	nao	\N
324	239	5	272	conduta	cosmiatria	[Conduta registrada via procedimentos]	1	2026-02-13 13:29:30.457625	nao	\N
325	243	5	279	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-02-13 18:38:59.014034	nao	\N
363	282	5	325	queixa	patologia	cicatriz hipertrofica no umbiogo\ndescamacao no couro cabeludo\ne melasma leve	\N	2026-02-26 14:04:05.921763	nao	\N
364	282	5	325	conduta	patologia	📋 RECEITA EMITIDA: indico laser cicatriz ascne	10	2026-02-26 14:04:05.967095	nao	\N
259	161	5	189	diagnostico	patologia	MELASMA FACIAL E EXTRAFACIAL	\N	2026-02-03 13:41:33.079522	nao	\N
326	243	5	279	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	0	2026-02-13 18:38:59.058493	sim	{"norwood": null, "previous_transplant": "sim", "transplant_location": "outro_servico", "case_type": "primaria", "body_hair": true, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": false, "crown": false, "complete": true, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": "ja tem um fut\\narea dodaora para 3000 3500\\nimpossivel cobrir tudo\\ntentar body hair que sera so barba"}
327	238	5	271	queixa	patologia	granuloma no piercing	\N	2026-02-13 18:39:27.514925	nao	\N
328	238	5	271	conduta	patologia	diprogenta e fentizol	0	2026-02-13 18:39:27.558666	nao	\N
329	262	5	300	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-13 18:40:32.02169	nao	\N
330	262	5	300	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-02-13 18:40:32.06548	nao	\N
331	246	5	282	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-02-19 13:20:21.626523	nao	\N
332	246	5	282	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	0	2026-02-19 13:20:21.691447	sim	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": false, "crown": false, "complete": true, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": "desenho conservador"}
333	247	5	283	queixa	patologia	coceira no  corpo	\N	2026-02-19 13:29:49.962026	nao	\N
334	247	5	283	diagnostico	patologia	pruruido por estresse e ressecamento\n nao tem lesao de pele	\N	2026-02-19 13:29:50.022411	nao	\N
335	247	5	283	conduta	patologia	📋 RECEITA EMITIDA:	8	2026-02-19 13:29:50.078578	nao	\N
336	249	5	286	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-02-19 19:52:57.620747	nao	\N
337	249	5	286	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n\n\n📋 RECEITA EMITIDA:	3	2026-02-19 19:52:57.678126	sim	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": true, "crown": false, "complete": false, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": ""}
338	252	5	289	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-02-19 20:11:11.587953	nao	\N
339	252	5	289	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n\n\n📋 RECEITA EMITIDA:	3	2026-02-19 20:11:11.644307	nao	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": false, "crown": false, "complete": false, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": ""}
340	248	5	285	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-19 20:30:43.062799	nao	\N
341	248	5	285	conduta	cosmiatria	[Conduta registrada via procedimentos]	1	2026-02-19 20:30:43.117276	nao	\N
342	256	5	294	queixa	patologia	QUEDA DE CABELO	\N	2026-02-20 14:43:45.961982	nao	\N
343	256	5	294	conduta	patologia	📋 RECEITA EMITIDA:\nQUEDA DE CABELO SEM SINAIS CLINICA EM USO DE TESTO NAO CONSEGUIU USAR A DUTASTERIDA\nNAOA CHO Q SEJA ACLVICIE SO QUEDA MESMO	0	2026-02-20 14:43:46.180392	nao	\N
344	254	5	292	queixa	cosmiatria	QUEDA DE CA	\N	2026-02-20 18:55:42.655096	nao	\N
345	254	5	292	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-20 18:55:42.700866	nao	\N
346	254	5	292	conduta	cosmiatria	[Conduta registrada via procedimentos]	1	2026-02-20 18:55:42.745983	nao	\N
347	257	5	295	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-20 18:57:25.764424	nao	\N
348	257	5	295	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-02-20 18:57:25.811879	nao	\N
349	103	5	302	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-20 18:59:27.12196	nao	\N
350	103	5	302	conduta	cosmiatria	[Conduta registrada via procedimentos]	1	2026-02-20 18:59:27.168149	nao	\N
351	261	5	299	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-20 19:28:15.663987	nao	\N
352	261	5	299	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-02-20 19:28:15.706974	nao	\N
353	265	5	305	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-25 12:57:28.859812	nao	\N
354	265	5	305	conduta	cosmiatria	📋 RECEITA EMITIDA:	7	2026-02-25 12:57:28.912254	nao	\N
355	268	5	308	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-25 14:06:00.990286	nao	\N
356	268	5	308	conduta	cosmiatria	[Conduta registrada via procedimentos]	1	2026-02-25 14:06:01.037713	nao	\N
357	267	5	307	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-25 14:33:36.638891	nao	\N
358	267	5	307	conduta	cosmiatria	📋 RECEITA EMITIDA:	12	2026-02-25 14:33:36.68335	nao	\N
359	271	5	311	queixa	patologia	calvicie  vem fazndo infiltracao capilar	\N	2026-02-25 20:38:58.329033	nao	\N
360	271	5	311	conduta	patologia	ifiltracao capilar	0	2026-02-25 20:38:58.37442	nao	\N
368	296	5	340	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\ninicio finasterida	0	2026-02-27 18:32:58.147324	nao	\N
371	305	5	349	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-27 19:36:04.208538	nao	\N
372	305	5	349	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-02-27 19:36:04.252145	nao	\N
386	286	5	329	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	0	2026-02-28 01:49:38.693946	sim	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": true, "crown": true, "complete": false, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": "Teste"}
375	306	5	350	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-27 19:57:05.742329	nao	\N
376	306	5	350	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-02-27 19:57:05.787138	nao	\N
377	302	5	346	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-27 19:57:36.926869	nao	\N
378	302	5	346	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-02-27 19:57:36.969938	nao	\N
5	11	5	23	anamnese	transplante_capilar	perda do recesso frontal mantem topete e coroa	\N	2025-11-27 18:06:51.173391	nao	\N
369	307	5	351	anamnese	transplante_capilar	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-27 18:43:09.172191	nao	\N
370	307	5	351	conduta	transplante_capilar	[Conduta registrada via procedimentos]	0	2026-02-27 18:43:09.219564	nao	{"norwood": "3V", "case_type": "primaria", "previous_transplant": "nao", "transplant_location": "N/A", "frontal": true, "crown": true, "complete": false, "complete_body_hair": false, "dense_packing": true, "surgical_planning_text": "Planejamento de restaura\\u00e7\\u00e3o da linha frontal e coroa com dense packing."}
379	300	5	\N	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-02-27 20:00:09.907245	nao	\N
380	300	5	\N	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	0	2026-02-27 20:00:09.951735	nao	\N
373	303	5	\N	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-02-27 19:45:43.721697	nao	\N
374	303	5	\N	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n\n\n📋 RECEITA EMITIDA:	4	2026-02-27 19:45:43.76229	nao	\N
385	286	5	329	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-02-28 01:49:38.651332	nao	\N
6	11	5	23	diagnostico	transplante_capilar	calvice grau 4	\N	2025-11-27 18:06:51.217635	nao	\N
7	11	5	23	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	2	2025-11-27 18:06:51.263633	nao	\N
226	138	5	165	queixa	patologia	nevo com padrao globular no couro cabeludo com assimetria	\N	2026-01-27 14:40:32.117353	nao	\N
227	138	5	165	conduta	patologia	faço exerese hj	0	2026-01-27 14:40:32.163397	nao	\N
228	135	5	162	queixa	patologia	furunculose ou paniculite pos enximas	\N	2026-01-27 14:41:42.490602	nao	\N
229	135	5	162	conduta	patologia	bactrin f 12/12 10 dias	0	2026-01-27 14:41:42.53526	nao	\N
232	140	5	167	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-01-27 18:35:08.999454	nao	\N
238	147	5	174	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-02 14:04:05.100411	nao	\N
239	147	5	174	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-02-02 14:04:05.149213	nao	\N
241	151	5	178	queixa	patologia	qa e ds	\N	2026-02-02 15:12:02.308183	nao	\N
242	151	5	178	diagnostico	patologia	qs \nqa\nds	\N	2026-02-02 15:12:02.353249	nao	\N
243	151	5	178	conduta	patologia	doctar\ntarfic\nsunfres oil conrtol	44	2026-02-02 15:12:02.398537	nao	\N
244	159	5	186	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-02 15:13:14.476448	nao	\N
245	159	5	186	conduta	cosmiatria	[Conduta registrada via procedimentos]	1	2026-02-02 15:13:14.519277	nao	\N
250	156	5	183	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-02 19:57:32.821816	nao	\N
251	156	5	183	diagnostico	cosmiatria	qs na face\nfibroma mole no gluteo\ncelulite\nespodnilite anquilosante me uso de ce e imnubiologico	\N	2026-02-02 19:57:32.865196	nao	\N
252	156	5	183	conduta	cosmiatria	[Conduta registrada via procedimentos]	1	2026-02-02 19:57:32.909864	nao	\N
253	160	5	187	queixa	patologia	verruga plantar	\N	2026-02-02 20:22:00.585965	nao	\N
254	160	5	187	conduta	patologia	nl	0	2026-02-02 20:22:00.630442	nao	\N
257	168	5	197	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-03 13:40:43.085081	nao	\N
258	168	5	197	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-02-03 13:40:43.129582	nao	\N
271	172	5	201	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-02-04 13:15:40.711414	nao	\N
272	172	5	201	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\nminoxidil 2,5	0	2026-02-04 13:15:40.758267	sim	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": false, "crown": false, "complete": false, "complete_body_hair": false, "dense_packing": true, "surgical_planning_text": "tem a hairline mantida cobrir as entradas"}
281	180	5	209	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-05 14:36:32.353814	nao	\N
282	180	5	209	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-02-05 14:36:32.399674	nao	\N
283	179	5	208	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-02-05 14:41:26.691791	nao	\N
284	179	5	208	conduta	transplante_capilar	FINASTEIRDA 5MG JA TOMA MINOXIDIL ORAL\nORIENTACAO GERAL	1	2026-02-05 14:41:26.737037	sim	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": true, "frontal": false, "crown": false, "complete": false, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": "PACIENTE QUER AUMENTO DE VOLUME E DIMNUICAO DA TESTA\\n PRA FAZER SEM RASPAR DEVERIA FAZER SO AIRLINE NAO FAZER VOLUME"}
285	182	5	211	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-05 18:01:03.243997	nao	\N
286	182	5	211	conduta	cosmiatria	[Conduta registrada via procedimentos]	12	2026-02-05 18:01:03.286141	nao	\N
287	181	5	210	queixa	patologia	ACNE	\N	2026-02-05 18:35:36.757942	nao	\N
288	181	5	210	diagnostico	patologia	ACNE LEVE	\N	2026-02-05 18:35:36.800712	nao	\N
289	181	5	210	conduta	patologia	USO DE EPIDUO	0	2026-02-05 18:35:36.843551	nao	\N
387	288	5	331	queixa	\N	Retoque de Botox na glabela e testa.	\N	2026-02-28 02:21:32.106145	nao	\N
388	288	5	331	conduta	\N	Realizado 25u de Botox. Retorno em 15 dias.	\N	2026-02-28 02:21:32.106167	nao	\N
389	288	5	331	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-28 19:56:17.561574	nao	\N
390	288	5	331	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-02-28 19:56:17.609039	nao	\N
391	297	5	341	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-02-28 21:12:31.384255	nao	\N
392	297	5	341	conduta	cosmiatria	[Conduta registrada via procedimentos]	1	2026-02-28 21:12:31.435468	nao	\N
393	308	5	352	queixa	patologia	papula  vegetante no membro superior diretio	\N	2026-03-02 12:32:25.998915	nao	\N
394	308	5	352	diagnostico	patologia	queratoacantoma\nou cec	\N	2026-03-02 12:32:26.051852	nao	\N
395	308	5	352	conduta	patologia	agendar exerese	0	2026-03-02 12:32:26.097245	nao	\N
396	310	5	354	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-03-02 13:15:40.731673	nao	\N
397	310	5	354	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	7	2026-03-02 13:15:40.777373	nao	\N
398	309	5	353	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-02 13:17:43.164831	nao	\N
399	309	5	353	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-03-02 13:17:43.208805	nao	\N
400	311	5	355	queixa	patologia	pele muito branca\n vem pra checkup	\N	2026-03-02 13:34:39.208719	nao	\N
401	311	5	355	conduta	patologia	nl verruga e orietacao\n\n📋 RECEITA EMITIDA:	6	2026-03-02 13:34:39.258431	nao	\N
402	313	5	357	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-03-02 13:50:54.995312	nao	\N
403	313	5	357	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	0	2026-03-02 13:50:55.03885	nao	\N
404	314	5	358	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-02 14:05:47.471371	nao	\N
405	314	5	358	conduta	cosmiatria	[Conduta registrada via procedimentos]	1	2026-03-02 14:05:47.517819	nao	\N
406	315	5	359	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-02 17:51:11.013708	nao	\N
407	315	5	359	conduta	cosmiatria	contorno so do lado direiot e 2 pontos de cada lado e mais de retro injejcao\nlado direto 0,7 lado e 0,2\n0,3 inferior\n1250	1	2026-03-02 17:51:11.06022	nao	\N
408	315	5	359	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-02 18:04:42.75393	nao	\N
409	315	5	359	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-03-02 18:04:42.797847	nao	\N
410	316	5	360	conduta	patologia	reotque botox 20 u	0	2026-03-02 19:17:36.728058	nao	\N
411	316	5	360	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-02 19:19:49.583509	nao	\N
412	316	5	360	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-03-02 19:19:49.627685	nao	\N
413	320	5	366	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-02 19:21:15.401316	nao	\N
414	320	5	366	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-03-02 19:21:15.442958	nao	\N
415	317	5	362	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-02 19:27:58.972274	nao	\N
416	317	5	362	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-03-02 19:27:59.016677	nao	\N
417	316	5	360	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-03-02 20:11:12.440783	nao	\N
418	316	5	360	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	27	2026-03-02 20:11:12.4933	nao	\N
419	318	5	363	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-03-02 20:33:14.204304	nao	\N
420	318	5	363	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n\n\n📋 RECEITA EMITIDA:	33	2026-03-02 20:33:14.248937	nao	\N
421	319	5	364	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-02 20:40:20.931134	nao	\N
422	319	5	364	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-03-02 20:40:20.975062	nao	\N
423	321	5	367	queixa	cosmiatria	queda de cabelo\nnevo na face\ndermatite seborreica couro cabeludo	\N	2026-03-03 12:52:05.887417	nao	\N
424	321	5	367	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-03 12:52:05.944404	nao	\N
425	321	5	367	conduta	cosmiatria	agendar exerese dos nevos 2500 3 nevos\n\n📋 RECEITA EMITIDA:	24	2026-03-03 12:52:05.988409	nao	\N
426	322	5	368	queixa	patologia	quedad e cabelo	\N	2026-03-03 13:09:53.833336	nao	\N
427	322	5	368	diagnostico	patologia	teve sarcopenia e queda de de cabelo em novembro\nhj  ta com com efluvio importante no exame fisico	\N	2026-03-03 13:09:53.87864	nao	\N
428	322	5	368	conduta	patologia	solicto exames\n📋 RECEITA EMITIDA:	0	2026-03-03 13:09:53.923408	nao	\N
429	324	5	370	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-03 13:47:58.400657	nao	\N
430	324	5	370	conduta	cosmiatria	📋 RECEITA EMITIDA:	4	2026-03-03 13:47:58.454954	nao	\N
431	323	5	369	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-03 14:04:21.015914	nao	\N
432	323	5	369	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-03-03 14:04:21.059471	nao	\N
433	325	5	371	queixa	patologia	queda de cabelo	\N	2026-03-03 14:14:44.572631	nao	\N
434	325	5	371	conduta	patologia	hipeceratose folicluar\ncalivcie inicial\n\n📋 RECEITA EMITIDA:	0	2026-03-03 14:14:44.616784	nao	\N
435	326	5	372	queixa	patologia	acne da mulher adulta\nusou yaz pele otima mas tinha dor de caberca\nhj esta com progesterona oral e espirono 100 3 meses com melhora	\N	2026-03-03 14:40:32.419787	nao	\N
436	326	5	372	conduta	patologia	📋 RECEITA EMITIDA:	13	2026-03-03 14:40:32.465644	nao	\N
437	334	5	381	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-03-03 18:25:12.244533	nao	\N
438	334	5	381	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n\n\n📋 RECEITA EMITIDA:	30	2026-03-03 18:25:12.288307	sim	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": true, "crown": false, "complete": false, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": "nao quer abaixar tanto a hairline\\nfazer apartir do que tem e abaixar um pouco das entradas"}
439	328	5	375	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-03 18:38:37.290714	nao	\N
440	328	5	375	conduta	cosmiatria	evo no dorso nasal\n\nmasi 2 glandulas sebaceas fazer exerese  e cauterizacao 1500\n\nindico limelght  e pearl maos 1000/ sessao\n radiesse maos\n\n\nUso Tópico\nAnti-Pigment Dual Sérum\naplicar no rosto À noite e retirar pela manhã\ncollagen specialist\naplicar no rosto pela manhã antes do fps\nHYDROBOOST GEL DE LIMPEZA NEUTROGENA\nLAVAR O ROSTO 2X/DIA POR DIA	1	2026-03-03 18:38:37.335777	nao	\N
441	330	5	377	queixa	patologia	espinhas e cravos	\N	2026-03-03 18:55:07.64696	nao	\N
442	330	5	377	diagnostico	patologia	acne leve	\N	2026-03-03 18:55:07.691598	nao	\N
443	330	5	377	conduta	patologia	📋 RECEITA EMITIDA: limpeza de pele e orientacao	0	2026-03-03 18:55:07.737042	nao	\N
444	335	5	382	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-03 19:17:45.224439	nao	\N
445	335	5	382	diagnostico	cosmiatria	nevos sem aleteracao a deramtoscopia	\N	2026-03-03 19:17:45.269555	nao	\N
446	333	5	380	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-03 20:31:55.510943	nao	\N
447	333	5	380	conduta	cosmiatria	[Conduta registrada via procedimentos]	14	2026-03-03 20:31:55.556609	nao	\N
448	333	5	380	conduta	patologia	📋 RECEITA EMITIDA:	0	2026-03-03 20:53:26.198944	nao	\N
449	229	5	392	queixa	patologia	ACNE E QUEDA DE CABELO	\N	2026-03-04 13:14:50.179159	nao	\N
450	229	5	392	anamnese	patologia	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-04 13:14:50.307446	nao	\N
451	229	5	392	conduta	patologia	NAO TEM NADA NO CABELO QUER APENAR DEIXAR MAIS CABELAO PASSO PIELUS DI PQ TEM UM POUCO DE CASPA\nPACIENTE QUER  INICIAR ISO\n\nSOLICITO EXAMES\nTEM ACNE DA MULHER ADULTA USA DIU  NAOQ UER USAR ACO\nVAMOS TENTAR ISO\n\n📋 RECEITA EMITIDA:	6	2026-03-04 13:14:50.351393	nao	\N
452	337	5	391	queixa	patologia	QA NA  TESTA E NA TEMPORA	\N	2026-03-04 13:27:03.761415	nao	\N
453	337	5	391	anamnese	patologia	NAO TEM SINAIS DE CC APENAS DE QA\n\nTEM PADRA DE ALOEPCIA FIBROSNATE FORNTAL\nSEM ATIVIDADE DA DOENCA NA DERMATOSCOPIA	\N	2026-03-04 13:27:03.804156	nao	\N
454	337	5	391	diagnostico	patologia	QA\nAFF	\N	2026-03-04 13:27:03.846404	nao	\N
455	337	5	391	conduta	patologia	📋 RECEITA EMITIDA:	0	2026-03-04 13:27:03.888695	nao	\N
456	338	5	393	queixa	cosmiatria	VERRUGA VULGAR NO COTOVELO	\N	2026-03-04 13:42:55.540482	nao	\N
487	366	5	423	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-03-05 19:40:32.785922	nao	\N
457	338	5	393	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-04 13:42:55.583939	nao	\N
458	338	5	393	conduta	cosmiatria	NL E ORIETANCOES\n\n📋 RECEITA EMITIDA:	11	2026-03-04 13:42:55.743299	nao	\N
459	341	5	396	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-04 15:00:01.961646	nao	\N
460	341	5	396	diagnostico	cosmiatria	DESIDROSE\nQS	\N	2026-03-04 15:00:02.005229	nao	\N
461	341	5	396	conduta	cosmiatria	Nome: ELIANE R HADDAD\n\nUso Tópico\n\n1.\nDIPROGENTA\n\nAPLICAR NAS LESOES 2X/DIA POR 5 DIAS\n\n2.\nEUCERIN Creme Hidratante para Pés Urea Repair Plus 100ml, Hidratação Intensiva, Ureia,\n\nAPLICAR NOS PES E NO COTOVELO 2X/DIA\n📋 RECEITA EMITIDA:	13	2026-03-04 15:00:02.049084	nao	\N
462	340	5	395	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-04 15:05:52.341543	nao	\N
463	340	5	395	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-03-04 15:05:52.385888	nao	\N
464	342	5	397	queixa	cosmiatria	ULTIMO BOTOX FOI OUTUBRO DE 25 VEM HJ PRA REFAZER	\N	2026-03-04 18:00:50.33152	nao	\N
465	342	5	397	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-04 18:00:50.375899	nao	\N
466	342	5	397	conduta	cosmiatria	EM USO DE \nISDIN HYALURRON FILLER\nH.A VICHY\nNEOVADIL\n\n📋 RECEITA EMITIDA:	20	2026-03-04 18:00:50.420064	nao	\N
467	343	5	398	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-03-04 18:27:04.876555	nao	\N
468	343	5	398	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n\n\n📋 RECEITA EMITIDA:	19	2026-03-04 18:27:04.920623	sim	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": false, "crown": false, "complete": true, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": "PRIORIDADE FRONTAL\\nSazer hairline conservadora com  entrada\\nchamar a esposa\\npaciente quer 80 frontal e 20 cora\\nta\\u00e7vez 60 40"}
469	345	5	400	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-03-04 19:06:10.173556	nao	\N
470	345	5	400	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	1	2026-03-04 19:06:10.222406	sim	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": true, "crown": false, "complete": false, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": "AREA DOADORA RUIM\\nTEM AREA DOARA PARA BODY HAIR EM UMA POSSIVEL CIRURGIA"}
471	347	5	402	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-04 19:33:51.57119	nao	\N
472	347	5	402	conduta	cosmiatria	[Conduta registrada via procedimentos]	7	2026-03-04 19:33:51.616063	nao	\N
473	346	5	401	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-03-04 19:57:40.158661	nao	\N
474	346	5	401	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	2	2026-03-04 19:57:40.204154	sim	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": false, "crown": true, "complete": false, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": "PACIENTE TEM PRIORIDADE COROA\\nFAZER 70 POR CENTO NA COROA\\n30 NA HAIRLINE MANTENDO EXATAMETNE A LINHA SEM AUMENTAR ENTRADAS PACIENTE BEM CONSERVADOR"}
475	356	5	411	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-04 19:58:32.544536	nao	\N
476	356	5	411	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-03-04 19:58:32.588298	nao	\N
477	358	5	414	queixa	patologia	verruga no queixo e no pe \nfaz uso de anticoagulante	\N	2026-03-05 12:41:57.211573	nao	\N
478	358	5	414	conduta	patologia	nl	0	2026-03-05 12:41:57.341371	nao	\N
479	360	5	417	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-03-05 14:15:17.885869	nao	\N
480	360	5	417	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n\n\n📋 RECEITA EMITIDA:\n\n\n📋 RECEITA EMITIDA:	7	2026-03-05 14:15:17.930575	nao	\N
481	374	5	433	queixa	patologia	queda de cabelo ha anos com afinamento	\N	2026-03-05 19:09:14.266668	nao	\N
482	374	5	433	anamnese	patologia	esta com uso de bitonina nutricoline e selenio de outra dermato com queda ativa de  cabelo no exame	\N	2026-03-05 19:09:14.312252	nao	\N
483	374	5	433	diagnostico	patologia	operou ha 1 semaa  mas ja estava com queda a mais tempo\n\ntem um pouco d ecalvicie feminina\ne sim tem efluvio telogeno	\N	2026-03-05 19:09:14.357706	nao	\N
484	374	5	433	conduta	patologia	minoxidil oral \nexames pra fver se precisa da soroterapia ev\n\n📋 RECEITA EMITIDA:	0	2026-03-05 19:09:14.402981	nao	\N
485	365	5	422	queixa	patologia	pintas naface quer  fazer cirurgia	\N	2026-03-05 19:24:03.221008	nao	\N
486	365	5	422	conduta	patologia	agendar exerese de 1 lesao para testar pq paciente ficou com medo do resultado 1800 1 lesao 2-3 2500	0	2026-03-05 19:24:03.272183	nao	\N
488	366	5	423	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n\n\n📋 RECEITA EMITIDA:	9	2026-03-05 19:40:32.841659	nao	\N
489	368	5	426	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-03-05 19:48:29.682812	nao	\N
490	368	5	426	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n\n\n📋 RECEITA EMITIDA:	7	2026-03-05 19:48:29.728486	sim	{"norwood": null, "previous_transplant": "sim", "transplant_location": "ICB", "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": false, "crown": false, "complete": false, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": "fazer o segundo abaixando a entrada e corrigindo o pico temporal tirei foto do desneho depois disso implemntar aumento da densidade na frente e 30 % a tras no maximo, apesar de precisar paciente quer prioridade frente e entradas"}
491	367	5	424	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-03-05 20:41:57.616748	nao	\N
492	367	5	424	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	0	2026-03-05 20:41:57.661984	nao	\N
493	369	5	427	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-05 20:49:11.17905	nao	\N
494	369	5	427	conduta	cosmiatria	[Conduta registrada via procedimentos]	5	2026-03-05 20:49:11.224335	nao	\N
495	377	5	436	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-03-06 13:28:32.682538	nao	\N
496	377	5	436	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n\n\n📋 RECEITA EMITIDA:\n acresecentei diprosalic pq teve alopecia areata 15 dias antes do transplante na rea doadora a esquerda atras da orleha	16	2026-03-06 13:28:32.727892	sim	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": true, "crown": false, "complete": false, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": "alta densidade so na frente"}
497	378	5	439	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-06 14:24:35.647616	nao	\N
498	378	5	439	diagnostico	cosmiatria	herpes zoster na face\nhj ja tratado com valaciclovir so faco orientacao	\N	2026-03-06 14:24:35.691771	nao	\N
499	378	5	439	conduta	cosmiatria	📋 RECEITA EMITIDA:	3	2026-03-06 14:24:35.73586	nao	\N
500	259	5	441	queixa	cosmiatria	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-03-09 13:14:15.850499	nao	\N
501	259	5	441	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-09 13:14:15.962503	nao	\N
503	379	5	440	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-03-09 13:25:47.089409	nao	\N
504	379	5	440	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n\n\n📋 RECEITA EMITIDA:	2	2026-03-09 13:25:47.133994	nao	\N
505	380	5	442	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-03-09 13:45:05.031498	nao	\N
506	380	5	442	anamnese	transplante_capilar	ALOPECIA TRAINGULAR VEERRUGA NA BARBA	\N	2026-03-09 13:45:05.075353	nao	\N
507	380	5	442	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\nFAÇO NL NA VERRUGA PASSO ADVANTAN PARA UM NEURODERMITE NO DEDAO DA MAO DIREITA QUE FOI TRATADA COMO VERRUGA\n HJ NAO TEM VERRUGA VULGAR NA MAO APENAS NA FACE\n\n📋 RECEITA EMITIDA:	5	2026-03-09 13:45:05.119349	nao	\N
508	238	5	443	conduta	patologia	📋 RECEITA EMITIDA:	0	2026-03-09 13:58:08.2536	nao	\N
509	381	5	444	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-03-09 14:24:35.240806	nao	\N
510	381	5	444	anamnese	transplante_capilar	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-09 14:24:35.284289	nao	\N
511	381	5	444	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n\n\n📋 RECEITA EMITIDA:	15	2026-03-09 14:24:35.327467	nao	\N
502	259	5	441	conduta	cosmiatria		36	2026-03-09 13:14:16.006123	nao	\N
512	383	5	447	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-03-09 19:55:21.228273	nao	\N
513	383	5	447	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n\n\n📋 RECEITA EMITIDA:	1	2026-03-09 19:55:21.274981	nao	\N
514	385	5	449	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-03-09 20:12:22.000893	nao	\N
515	385	5	449	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n\n\n📋 RECEITA EMITIDA:	3	2026-03-09 20:12:22.051734	nao	\N
516	387	5	451	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-09 20:25:42.995989	nao	\N
517	387	5	451	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-03-09 20:25:43.041001	nao	\N
518	382	5	446	anamnese	cosmiatria	paciente fez em salvador argo plasma e morphues full body\nquer continuar a fazer mais sessoes	\N	2026-03-10 11:38:54.629695	nao	\N
519	382	5	446	conduta	cosmiatria	[Conduta registrada via procedimentos]	2	2026-03-10 11:38:54.67658	nao	\N
520	390	5	455	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-10 13:07:18.221263	nao	\N
521	390	5	455	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-03-10 13:07:18.267193	nao	\N
524	396	5	461	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-03-10 18:24:10.812307	nao	\N
525	396	5	461	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	0	2026-03-10 18:24:10.85484	sim	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair_needed": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": false, "crown": true, "complete": false, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": "quer desenho bem agressivo", "clinical_conduct": "O transplante capilar \\u00e9 uma etapa do tratamento e n\\u00e3o o tratamento completo. \\u00c9 fundamental a ades\\u00e3o ao acompanhamento cl\\u00ednico para manuten\\u00e7\\u00e3o dos resultados. O sucesso cir\\u00fargico depende do controle cont\\u00ednuo da queda capilar e da resposta individual do paciente ao tratamento.\\n\\n"}
526	393	5	458	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-10 18:40:59.710404	nao	\N
527	393	5	458	conduta	cosmiatria	📋 RECEITA EMITIDA:	3	2026-03-10 18:40:59.757971	nao	\N
528	394	5	459	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-10 18:52:43.003699	nao	\N
529	394	5	459	conduta	cosmiatria	📋 RECEITA EMITIDA:	3	2026-03-10 18:52:43.051717	nao	\N
530	392	5	457	queixa	patologia	mae teve melanonam ha 10 anos	\N	2026-03-10 19:06:33.681674	nao	\N
531	392	5	457	anamnese	patologia	exame  sem alteracoes	\N	2026-03-10 19:06:33.725622	nao	\N
532	392	5	457	conduta	patologia	dermatoscopia ok\ntem acne falo de pearl fracionado	1	2026-03-10 19:06:33.769218	nao	\N
533	392	5	457	conduta	patologia	📋 RECEITA EMITIDA:	0	2026-03-10 19:11:35.58392	nao	\N
534	395	5	460	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-03-10 19:44:49.779305	nao	\N
535	395	5	460	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n\n\n📋 RECEITA EMITIDA:	20	2026-03-10 19:44:49.824127	sim	{"norwood": "3", "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair_needed": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": false, "crown": false, "complete": true, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": "manter a hairline tinha v pico de viuva\\n\\naumentar a densidade 60 frontal", "clinical_conduct": "O transplante capilar \\u00e9 uma etapa do tratamento e n\\u00e3o o tratamento completo. \\u00c9 fundamental a ades\\u00e3o ao acompanhamento cl\\u00ednico para manuten\\u00e7\\u00e3o dos resultados. O sucesso cir\\u00fargico depende do controle cont\\u00ednuo da queda capilar e da resposta individual do paciente ao tratamento.\\n\\n\\n\\n\\ud83d\\udccb RECEITA EMITIDA:\\n"}
536	219	5	463	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-11 13:01:39.161976	nao	\N
537	219	5	463	conduta	cosmiatria	[Conduta registrada via procedimentos]	1	2026-03-11 13:01:39.208069	nao	\N
538	411	5	484	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-03-11 13:21:35.551022	nao	\N
539	411	5	484	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.\n\n\n\n📋 RECEITA EMITIDA:	7	2026-03-11 13:21:35.597889	sim	{"norwood": "3", "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair_needed": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": false, "crown": false, "complete": true, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": "", "clinical_conduct": "O transplante capilar \\u00e9 uma etapa do tratamento e n\\u00e3o o tratamento completo. \\u00c9 fundamental a ades\\u00e3o ao acompanhamento cl\\u00ednico para manuten\\u00e7\\u00e3o dos resultados. O sucesso cir\\u00fargico depende do controle cont\\u00ednuo da queda capilar e da resposta individual do paciente ao tratamento.\\n\\n\\n\\n\\ud83d\\udccb RECEITA EMITIDA:\\n"}
540	398	5	464	queixa	patologia	checkup	\N	2026-03-11 13:37:14.153275	nao	\N
541	398	5	464	anamnese	patologia	muito foto exposicao\ntem nevos na face com alteracao dosol	\N	2026-03-11 13:37:14.198912	nao	\N
542	398	5	464	conduta	patologia	📋 RECEITA EMITIDA:	2	2026-03-11 13:37:14.245354	nao	\N
543	412	5	485	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-11 15:26:06.126979	nao	\N
544	412	5	485	diagnostico	cosmiatria	verruga vulgar nas costas\n onicomicose\n nevos sem alteracaoa dermatoscopia	\N	2026-03-11 15:26:06.17119	nao	\N
545	412	5	485	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-03-11 15:26:06.215781	nao	\N
546	399	5	466	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-03-11 15:26:53.855811	nao	\N
547	399	5	466	conduta	transplante_capilar	ja usa finasterida	0	2026-03-11 15:26:53.908036	sim	{"norwood": "2", "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair_needed": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": true, "crown": false, "complete": false, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": "manter a hairline aumentar a densidade", "clinical_conduct": "ja usa finasterida"}
548	135	5	465	queixa	patologia	furunculos no corpo	\N	2026-03-11 18:14:02.005089	nao	\N
549	135	5	465	anamnese	patologia	multiplas furunculos de repeticao profundas coma trofia	\N	2026-03-11 18:14:02.060352	nao	\N
550	135	5	465	conduta	patologia	tratei combactrinf 12/12 30 dias melhora parcial 10 dia de pred melhora parcial\nagendar exerese\npara biopsia eritemanodoso	1	2026-03-11 18:14:02.107765	nao	\N
551	400	5	469	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-03-11 18:41:07.833497	nao	\N
552	400	5	469	conduta	transplante_capilar	inicio ja minoxidil oral\n\n📋 RECEITA EMITIDA:	1	2026-03-11 18:41:07.88019	sim	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair_needed": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": false, "crown": false, "complete": true, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": "quer um desenho bem agressivo\\n mas ja esta precisando no escalpe  e coroa\\n indico um densenho abaixando mais as entradas que a hairline\\n70 frontal", "clinical_conduct": "inicio ja minoxidil oral\\n\\n\\ud83d\\udccb RECEITA EMITIDA:\\n"}
553	413	5	486	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-03-11 19:13:24.957543	nao	\N
554	413	5	486	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	0	2026-03-11 19:13:25.00616	sim	{"norwood": "3", "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair_needed": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": false, "crown": false, "complete": true, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": "fazer frontal abaixando 1 dedo coroa e fazer denso\\ntambem o resto patchwork", "clinical_conduct": "O transplante capilar \\u00e9 uma etapa do tratamento e n\\u00e3o o tratamento completo. \\u00c9 fundamental a ades\\u00e3o ao acompanhamento cl\\u00ednico para manuten\\u00e7\\u00e3o dos resultados. O sucesso cir\\u00fargico depende do controle cont\\u00ednuo da queda capilar e da resposta individual do paciente ao tratamento.\\n\\n"}
555	402	5	471	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-03-11 19:23:00.917402	nao	\N
556	402	5	471	conduta	transplante_capilar	tem uma calvicie evidente na coroa\nmas nao se incomoda\ntem rarefacao na frente e ano se incomoda\nprefere iniciar tratamento\ntiro foto  na maquina\n\n📋 RECEITA EMITIDA:	6	2026-03-11 19:23:00.963404	nao	{"norwood": "2", "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair_needed": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": false, "crown": false, "complete": false, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": "", "clinical_conduct": "tem uma calvicie evidente na coroa\\nmas nao se incomoda\\ntem rarefacao na frente e ano se incomoda\\nprefere iniciar tratamento\\ntiro foto  na maquina\\n\\n\\ud83d\\udccb RECEITA EMITIDA:\\n"}
557	382	5	\N	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-03-12 12:22:11.306911	nao	\N
558	404	5	473	queixa	patologia	paciente com esclerodermia no tronco	\N	2026-03-12 12:41:30.888666	nao	\N
559	404	5	473	anamnese	patologia	placa na area infra mamaria	\N	2026-03-12 12:41:30.9339	nao	\N
560	404	5	473	conduta	patologia	tratou desde 2024 comigo em uso de mtx\nhj estou tirando o mtx e iniciando o tarfic 0,1\n\n📋 RECEITA EMITIDA:	8	2026-03-12 12:41:30.979419	nao	\N
561	404	5	473	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-12 12:44:38.487307	nao	\N
562	404	5	473	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-03-12 12:44:38.533806	nao	\N
563	405	5	474	queixa	transplante_capilar	Paciente refere queixa de rarefação capilar e calvície progressiva.	\N	2026-03-12 13:44:44.168134	nao	\N
564	405	5	474	conduta	transplante_capilar	O transplante capilar é uma etapa do tratamento e não o tratamento completo. É fundamental a adesão ao acompanhamento clínico para manutenção dos resultados. O sucesso cirúrgico depende do controle contínuo da queda capilar e da resposta individual do paciente ao tratamento.	1	2026-03-12 13:44:44.213061	nao	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair_needed": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": false, "crown": false, "complete": false, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": "", "clinical_conduct": "O transplante capilar \\u00e9 uma etapa do tratamento e n\\u00e3o o tratamento completo. \\u00c9 fundamental a ades\\u00e3o ao acompanhamento cl\\u00ednico para manuten\\u00e7\\u00e3o dos resultados. O sucesso cir\\u00fargico depende do controle cont\\u00ednuo da queda capilar e da resposta individual do paciente ao tratamento.\\n\\n"}
565	405	5	474	conduta	transplante_capilar	📋 RECEITA EMITIDA:	0	2026-03-12 13:54:53.066502	nao	{"norwood": null, "previous_transplant": "nao", "transplant_location": null, "case_type": "primaria", "body_hair_needed": false, "eyebrow_transplant": false, "beard_transplant": false, "feminine_hair_transplant": false, "frontal": false, "crown": false, "complete": false, "complete_body_hair": false, "dense_packing": false, "surgical_planning_text": "", "clinical_conduct": "\\n\\n\\ud83d\\udccb RECEITA EMITIDA:\\n"}
566	61	5	476	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-12 17:57:29.768954	nao	\N
567	61	5	476	conduta	cosmiatria	1 ampola ck1 ck3  rennova\ne 1 ampola contonro queixo jw4 e jw5 volyme	1	2026-03-12 17:57:29.877975	nao	\N
568	363	5	477	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-12 17:59:08.586359	nao	\N
569	363	5	477	conduta	cosmiatria	[Conduta registrada via procedimentos]	1	2026-03-12 17:59:08.63163	nao	\N
570	420	5	492	queixa	cosmiatria	erritnia baixa 45\n\ninidco vitamina ev e ferro ev\n\nqueda ativa	\N	2026-03-12 18:36:27.646276	nao	\N
571	420	5	492	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-12 18:36:27.690758	nao	\N
572	420	5	492	conduta	cosmiatria	erritnia baixa 45\n\ninidco vitamina ev e ferro ev\n\nqueda ativa	1	2026-03-12 18:36:27.739869	nao	\N
573	408	5	479	queixa	patologia	queda de cabelo e rarefacao capilar	\N	2026-03-12 19:17:06.393839	nao	\N
574	408	5	479	anamnese	patologia	sem queda na tracao\n mas um afinamento bem evidente na regiao central	\N	2026-03-12 19:17:06.439392	nao	\N
575	408	5	479	conduta	patologia	📋 RECEITA EMITIDA:\nnunca trattou avaliar primeiro resposta do tratamento pra depois ver o transplante	0	2026-03-12 19:17:06.484554	nao	\N
576	224	5	480	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-12 19:19:10.93369	nao	\N
577	224	5	480	conduta	cosmiatria	fez dia 11/2 limeght 20 face\n\nhj faco 2° sessao 22j	1	2026-03-12 19:19:10.988874	nao	\N
578	419	5	491	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-12 19:59:03.401552	nao	\N
579	419	5	491	conduta	cosmiatria	📋 RECEITA EMITIDA:	5	2026-03-12 19:59:03.445099	nao	\N
580	419	5	491	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-12 19:59:14.713203	nao	\N
581	419	5	491	conduta	cosmiatria	📋 RECEITA EMITIDA:	0	2026-03-12 19:59:14.760689	nao	\N
582	404	5	473	anamnese	cosmiatria	Paciente refere queixas cosmiátricas, buscando melhora da qualidade da pele. Sem queixas de doenças dermatológicas ativas.	\N	2026-03-12 20:16:59.667449	nao	\N
583	404	5	473	conduta	cosmiatria	[Conduta registrada via procedimentos]	0	2026-03-12 20:16:59.711275	nao	\N
\.


--
-- Data for Name: operating_room; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.operating_room (id, name, capacity, created_at) FROM stdin;
1	Sala 1	1	2025-12-12 18:08:20.996631
\.


--
-- Data for Name: patient; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.patient (id, name, phone, email, birth_date, cpf, address, patient_type, attention_note, created_at, city, mother_name, indication_source, occupation, state, zip_code, has_transplant_indication, photo_url, ivp_stars, ivp_manual_override, ivp_updated_at, weight, height, blood_type, allergies, smoker) FROM stdin;
2	FERNANDA FERRARINI GOMES DA COSTA			\N	\N	\N	particular	\N	2025-11-25 18:11:56.698774	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
3	RENATO ZUPPANI	\N		2025-11-25	\N	\N	particular	\N	2025-11-25 18:34:26.994612	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
4	MARIA CRISTINA ALVES PEREIRA	\N		\N	\N	\N	particular	\N	2025-11-25 18:35:44.236781	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
5	SHIRLEY MARLENE DE SOUZA	\N		1957-08-06	00572548850	\N	particular	\N	2025-11-26 11:39:29.12012	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
6	LUIS HENRIQUE RONCARI JUNIOR			\N	\N	\N	particular	\N	2025-11-26 12:42:25.307939	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
7	RAFAEL FERNANDO ZAMBON	\N		\N	\N	\N	particular	\N	2025-11-26 12:43:30.703368	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
8	JOAO PAULO EUGENIO DA SILVA	\N		\N	\N	\N	particular	\N	2025-11-26 12:44:20.726762	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
9	TAUANE QUEIROZ	\N		\N	\N	\N	particular	\N	2025-11-26 12:45:43.347557	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
10	LEANDRO FELICIO NEVES	\N		\N	\N	\N	particular	\N	2025-11-26 18:01:37.584355	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
44	RENAN BECKER	16981262701		\N	\N	\N	particular	fazer frontal manter a hairline fazer apenas um pouco entrada	2025-12-09 15:33:49.741428	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
42	EDUARDO KAZUO	17981892099		\N	\N	\N	particular	\N	2025-12-09 15:30:37.24557	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
13	LUANA	\N		\N	\N	\N	particular	\N	2025-11-27 17:19:46.146407	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
14	ALEXANDRE	\N		\N	\N	\N	particular	\N	2025-11-27 17:20:34.899455	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
59	SABIE AP.CALIL TANNUS	16999921558	\N	1946-12-04	19179529887	\N	particular	\N	2025-12-11 11:55:24.466942	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
15	ARISLILIAN RAGOZONE CONRADO	\N		1972-05-15	\N	AV FLORIANO PEIXOTO 611	particular	\N	2025-11-28 12:33:12.87387	IPUA	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
11	EDUARDO DE BARROS CORREIA			1980-01-18	28646201899	RUA CORONEL LUIS DA SILVA BATISTA 910 AP 32	particular	TCC 	2025-11-27 12:46:46.217631	RIBEIRAO PRETO	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
16	ANA MARIA AFONSO GEORGETE	\N		1955-02-16	13865375863	\N	particular	\N	2025-11-28 15:56:09.599941	SERTAOZINHO	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
17	ADRIANA DA SILVA.	16997133625		1971-07-26	\N	\N	particular	\N	2025-11-28 19:51:20.118334	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
36	RITA DE CASSIA ALCIDES	\N		\N	\N	\N	particular	\N	2025-12-05 12:47:41.737604	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
41	ROGILSON	\N	\N	1968-12-10	18087678885	\N	particular	\N	2025-12-09 15:29:38.140113	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
18	DEBORA MARIANO GOMES DA SILVA	\N		\N	\N	\N	particular	\N	2025-12-02 12:34:34.925397	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
19	LAIS GONÇALVES BETINE	16997329354		1995-05-02	\N	RUA: PEDRO PEGORARO 626 AP32	particular	\N	2025-12-02 12:39:53.586515	ribeirao preto	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
21	JULIANA WEBBER CALDANA	18981914228		1986-11-14	 05804080946	\N	particular	\N	2025-12-02 12:48:37.046324	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
22	ROBERTA DE OLIVEIRA MARIANO	16997979993		1973-11-28	17552916800	\N	particular	\N	2025-12-02 12:50:06.51826	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
23	RODRIGO VILELA	\N		\N	\N	\N	particular	\N	2025-12-02 12:50:22.170006	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
24	WALTER BIAGI			\N	\N	\N	particular	\N	2025-12-02 12:52:02.387962	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
37	LUCAS ALMEIDA COSTA	\N		\N	\N	\N	particular	\N	2025-12-05 12:48:25.644368	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
25	PATRICIA HOPP	16981564444		\N	\N	\N	particular	\N	2025-12-02 12:53:49.527158	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
26	SOPHIA CIMATTI BELENTANI	\N		2007-07-19	45039935854	AV CARLOS EDUARDO DE GASPARI CONSONI 1900 CASA 107	particular	\N	2025-12-02 13:00:39.098588	RIBEIRAO PRETO	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
20	FERNANDES DIAS DE SOUZA			1978-11-24	\N	RUA MARTINHO JOSE MEGUELLE 35 	particular	calvicie muito extensa\narea doadora ruim\npenso em 2500 capilar \n1000 barba e 2000 peito\n\nainda sim ficara ralo com desenho conservador	2025-12-02 12:47:01.543319	ribeirao preto	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
27	TAISA MAGNANI	\N		\N	\N	\N	particular	\N	2025-12-03 12:27:10.17316	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
29	MANUELA RUIZ	\N		2011-02-02	\N	\N	particular	\N	2025-12-03 12:33:41.396973	\N	\N	PAI CRISTIANO	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
50	DANIELA VELLUDO SPADONI	\N		1986-09-08	35068974897	\N	particular	\N	2025-12-10 15:36:13.504362	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
31	SILVIA BIAGI DINIZ JUNQUEIRA	1691591482		1985-09-05	34673701879	AV ERACLITO FONTOURA SOBRAL PINTO 351 CS 77	particular	\N	2025-12-03 12:40:49.841786	\N	NEUSA BIAGI	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
32	LAYLLA CRISTHINE DE ALMEIDA REZENDE	16992008092		1989-07-22	09773577678	RUA: VIA JOAO BATISTA ASNATANA 215 BLOCO 21 AP 404	particular	\N	2025-12-03 12:43:55.905226	RIBEIRAO PRETO 	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
33	MAYARA MARINA MELO E GUIAO	1691338422		1980-07-05	09595807788	ROD SP 333 KM 312  CS 7 	particular	\N	2025-12-03 18:25:58.252886	RIBEIRAO PRETO 	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
30	MARCELO MINIKOWSKI	\N		1975-08-21	84743522900	AV LUIS EDUARDO TOLEDO PRADO 4100 QD 3 LOTE 3	particular	\N	2025-12-03 12:37:03.687714	RIBEIRAO PRTEO 	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
28	CASSIO FLORIANO			\N	\N	\N	particular	\N	2025-12-03 12:29:53.668149	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
34	LARA FERRAZ.	16992214406		\N	\N	\N	particular	\N	2025-12-04 13:48:50.03253	\N	\N	dr.filipe	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
35	ALICE SANCHES ALMEIDA14/08/2014			2014-08-14	\N	\N	particular	\N	2025-12-04 18:07:40.484753	\N	CRISTINA SANCHES PASSOS ANGELI ALMEIDA	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
38	MARCELO EDUARDO LAMARCA PALENCIANO	16997486685	\N	1970-04-30	13882487860	ANTONIO PEDRO 3368	particular	fez ha 1 ano fazer os egundo dando preferencia para coroa	2025-12-05 12:52:27.596701	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
39	HUGO BRANQUINHO DE CARVALHO	16997349659		\N	33408113858	R JOSE DE ALENCAR 1741 AP 62	particular	\N	2025-12-05 13:16:17.482333	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
40	PATRICIA CARVALHO UZUM	\N		\N	\N	\N	particular	\N	2025-12-05 17:44:38.782523	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
57	PATRICIA MARIA MONTANARI	16997350472		1977-10-06	27255431852	renato alves godoy 100 ap 122	particular	fazer o transpalnte na menor area possivel\n areadoadora ruim\nmuito fino ralo pensei 2000-2500\nfeminino	2025-12-10 18:11:18.096589	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
43	MARIA CRISTINA ALVES PEREIRA.	\N		\N	\N	\N	particular	\N	2025-12-09 15:32:36.64621	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
45	LIVIA PIOLI NAILS	\N		\N	\N	\N	particular	\N	2025-12-09 15:34:12.041899	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
48	LUCY APARECIDA DE OLIVEIRA	35988319620		1965-04-05	48451096620	PAULO DUARTE GUEDES 153 	particular	\N	2025-12-09 17:50:41.445208	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
49	VALDACIRA AP GUARNIERI	16999960932	\N	1969-01-17	11432131818		particular	\N	2025-12-09 18:18:15.15466					\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
47	JACIRA GUARNIERI	16981928586	\N	1953-01-24	14955941818		particular	\N	2025-12-09 15:35:21.586312					\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
61	POLLYANNA BOLINI MORETTI	16997070668		1991-12-16			particular	\N	2025-12-11 13:37:59.276916					\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
58	LAURA LETICIA PEREZ BECK	16988642225		1998-04-08	40653723806	AV SAO PAULO 160	particular	\N	2025-12-11 11:52:16.086182	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
53	FRANCISCO PACHECO	\N		\N	\N	\N	particular	\N	2025-12-10 15:39:11.395625	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
56	HENRIQUE CANDIA VICENTE AZEVEDO	16997601701		1986-01-10	32509166840	\N	particular	\N	2025-12-10 15:41:58.835086	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
51	JESSICA MAGANHA	16991785163	\N	1994-08-23	39620499832	\N	particular	\N	2025-12-10 15:37:13.921173	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
55	REGINALDO MARQUES			\N	\N	\N	particular	\N	2025-12-10 15:40:47.584769	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
52	IURI SVERZUT BELLESINI	16991777283		1982-05-03	29961601858	\N	particular	\N	2025-12-10 15:38:44.746421	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
60	SUELEN APARECIDA DACANAL DE SOUSA	\N		1982-09-23	\N	AV DEPUTADO SERGIO CARDOSO DE ALMEIDA 1980 AP 105	particular	\N	2025-12-11 13:28:09.699099	RIBEIRAO PRETO 	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
64	MELINA PEDEZZI LANDI	1992057448		1982-03-11	29168484879	\N	particular	\N	2025-12-11 18:15:15.902965	\N	MARIA ANGELICA DONDA PEDEZZI	\N	PUBLICITARIA	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
65	CRISTIANI FAVARO GONÇALVES GAZONI	16992132224		1967-06-12	\N	\N	particular	\N	2025-12-11 19:07:40.018352	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
66	LUIS CARLOS GONÇALVES.	1616833789894		\N	16833789894	\N	particular	\N	2025-12-12 12:25:14.407822	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
63	WANIA CARLA MARTINS CORREA	16981638592		1961-10-03	27998409819	\N	particular	\N	2025-12-11 17:57:52.641165	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
46	ANA FLAVIA MENDONÇA		\N	1985-07-31	41683204808		particular	\N	2025-12-09 15:34:59.014536					\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
54	ADRIANA APARECIDA MELO.	16988458645	\N	1986-09-04	\N	\N	particular	\N	2025-12-10 15:40:21.190815	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
62	ROSANA M MAGDALENA	1697415916		1961-09-09	10180092804		retorno	\N	2025-12-11 14:53:38.487671					\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
67	PALOMA DE KASSIA QUATRINI	\N		\N	\N	\N	particular	\N	2025-12-12 12:26:54.438851	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
68	LIVIA CALUZ ULIAN	\N		1984-08-08	30786958839	\N	particular	\N	2025-12-12 12:27:55.074776	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
69	CARLOS JOSE PEREIRA	\N		\N	\N	\N	particular	\N	2025-12-12 12:29:36.41196	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
71	MARY ARANTES WIERMANN BARROSO.	\N		\N	\N	\N	particular	\N	2025-12-12 12:37:10.607612	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
70	EDNA BURRONE B. DO NASCIMENTO	\N		0046-06-21	\N	\N	particular	\N	2025-12-12 12:30:39.476851	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
72	WILIAN CAMARGO DA COSTA	16991864326		1986-06-07	33980305805	\N	particular	\N	2025-12-12 12:40:44.7523	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
73	MARIA DO CARMO ANTONIALLI MARINO	19993633038		1961-12-25	04282315865	\N	particular	\N	2025-12-12 12:42:01.389903	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
76	GUSTAVO HENRIQUE SIGOLINE	11983858900		\N	32389354882	\N	particular	\N	2025-12-12 18:33:51.988314	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
77	SILMARA PADOVAN SPAZIANE	\N		\N	\N	\N	particular	\N	2025-12-12 18:34:33.082675	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
78	JULIANA CRISTINA SPAZIANI PANE.	\N		\N	\N	\N	particular	\N	2025-12-12 18:35:03.969057	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
79	ELIANE R HADDAD	\N		\N	\N	\N	particular	\N	2025-12-12 18:39:59.966995	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
81	MARTA CONCEIÇAO TOSTA	\N		\N	\N	\N	particular	\N	2025-12-12 19:49:20.544699	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
75	DOUGLAS FIOCHIO	\N		\N	\N	\N	particular	\N	2025-12-12 18:08:20.745052	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
82	FABIOLA MOREIRA ANDRADE	16981714155		1969-04-16	\N	RUA GARIBALDI 580 AP 73	particular	\N	2025-12-15 12:53:26.799581	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
83	ERIKA VILLAR S. FORTES GUIMARAES	\N		\N	\N	\N	particular	\N	2025-12-15 12:54:51.087808	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
84	LIVIA GALVANI DE BARROS CRUZ.	\N		1987-03-27	33819541802	AV HERACLITO FONTOURA SOBRAL PINTO 551 CASA 49	particular	\N	2025-12-15 13:00:23.286301	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
85	JULIANA BENASSI SANTON.	\N		\N	\N	\N	particular	\N	2025-12-15 13:02:28.298568	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
86	MARCIA CRISTINA GUEDES JANUARIO	16997530150		1975-11-02	\N	\N	particular	\N	2025-12-15 13:10:12.924612	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
117				1986-01-29	34232334866	RUA CARLOS RATELI CURY 697 CASA 69	UNIMED	\N	2026-01-22 14:23:53.54203	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
87	MARIA APARECIDA BIANCHI	\N		1950-11-27	55140408872	HUMITA 461 AP 112	particular	\N	2025-12-15 13:25:06.222969	RIBEIRAO PRTEO 	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
88	MARIA AUGUSTA BIANCHI	16992552414		1950-11-27	55140408872	\N	particular	\N	2025-12-15 13:28:54.934031	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
90	HERIKA CARDOSO LEITE	16991018111		1979-01-10	\N	CATARINA PAGLIESI MOBIGLIA 880	particular	\N	2025-12-15 13:33:31.687602	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
91	DAVI DELLA	\N		\N	\N	\N	particular	\N	2025-12-15 13:34:12.995125	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
80	SERGIO EDUARDO	16996424849		1977-09-23	20062728881	\N	particular	\N	2025-12-12 18:42:30.547208	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
92	JOSE ADEMIR FERRAO	\N		\N	74429159815	RUA GERMANO MOREIRA 706 	particular	\N	2025-12-15 13:35:47.186071	BATATAIS 	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
89	PAULO CESAR AP CINTRA	\N		1979-12-04	03650657651	\N	particular	\N	2025-12-15 13:31:29.845218	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
94	BRUNA BETTIOL ORTEIRO	16999945474		\N	\N	\N	particular	\N	2025-12-16 13:23:12.361717	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
1	CAROLINA CARVALHO BASILE	\N		1982-07-25	\N	wilson del vechio 304	particular	\N	2025-11-25 18:00:29.838492	RIBEIRAO PRETO	\N	Marido	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
98	MARIA JOSE BASTO DA S. MATSUMOT	1681223086		1964-07-29	10118965832	RUA CAMPOS SALES 183 AP 131	particular	\N	2026-01-19 17:16:54.041822	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
100	MARCELO C. TAZINAFFO	\N		1988-04-03	\N	R 3 361	particular	\N	2026-01-19 17:36:24.013221	orlandia 	ESTELA TAZINAFO	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
101	LAERCIO ERNESTO DE SOUZA	16996144441		1955-12-06	24905941091	\N	particular	\N	2026-01-21 13:00:05.566188	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
104	LUCIANA ABEID RIBEIRO DALMAGRO	16981216205		1986-01-24	\N	RUA GUILHERME FANTACINE 248	particular	\N	2026-01-21 14:19:36.48839	BATATAIS	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
96	CLAUDIA REGINA MONASSI KEDIA	16992352682		1971-05-26	14553370808	AV PROFESSOR JOAO FIUSA 209 AP 262	particular	\N	2025-12-16 13:27:25.359788	RIBEIRAO PRETO 	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
109	BRUNO CESAR LEDO	\N		\N	\N	\N	particular	\N	2026-01-21 14:49:37.098846	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
110	NILSON MANHANI	\N		\N	\N	\N	particular	\N	2026-01-21 14:51:04.237044	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
111	ERIKA VENANCIO	\N		\N	\N	\N	particular	\N	2026-01-21 14:51:30.088462	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
112	VANDER PAVAO	\N		\N	\N	\N	particular	\N	2026-01-21 14:51:49.629727	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
102	ANDERSON MOREIRA ZANON TENORIO	16991816584		1981-04-28	30793168864	AV LEAO XII 3900 AP 16018 A 	particular	\N	2026-01-21 13:08:17.898927	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
107	PEDRO ROBERTO	19992802777		\N	\N	\N	particular	\N	2026-01-21 14:48:38.895538	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
108	WILHIAN SANTOS	\N		\N	\N	\N	particular	\N	2026-01-21 14:49:10.702342	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
113	SEFORAH MARINA PACIFICO MANFRIM CONEGLIAN	16981012521		1977-01-22	17544263878	RUA: DR MARIO DE ASSIS MOURA 480 AP 54 B	particular	\N	2026-01-22 12:13:21.492416	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
114	RAFAEL MANFRIN CONEGLIAN	16981012521		2018-08-09	55544728852	DR. MARIO DE ASSIS MOURA 280 AP 54 B 	particular	\N	2026-01-22 12:25:09.08233	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
115	GEANE ESTELA AKOS	\N		1983-01-02	\N	\N	particular	\N	2026-01-22 12:52:54.847727	RIBEIRAO PRETO	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
97	ANDERSON ALEFANTE	16991872963		1979-02-10	27823719835	RUA SOLDADO ELISEU DOS SANTOS 60	particular	\N	2026-01-19 15:36:28.3023	ribeirao preto 	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
116	AMANDA BARBOSA	\N		\N	\N	\N	particular	juiza	2026-01-22 14:11:19.256104	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
130	ANA LIGIA SANTOS DE OLIVEIRA 	\N		1987-06-19	32294740823	\N	particular	\N	2026-01-26 17:47:23.080677	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
119	manuela melani	\N		\N	\N	\N	unimed	\N	2026-01-23 17:28:42.220852	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
121	ISABEL CRISTINA DE SOUSA MIACHON.	\N		\N	135538538-59	\N	particular	\N	2026-01-23 17:43:15.973455	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
122	NILSON CARLOS MANHANI	\N		\N	135538538-59	\N	retorno	\N	2026-01-23 17:44:04.920376	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
123	MARIA EDUARDA S MIACHON 	\N		\N	135538538-59	\N	unimed	\N	2026-01-23 17:45:07.408928	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
120	ALLAN RICARDO CARUSO 	\N		1973-05-27	32582852848	\N	retorno	@#$\n2000 frontal sem peninsulas, basicamente manter desenho\n1500 coroa\n	2026-01-23 17:30:07.035964	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
124	CRISLAINE JAMARINO 	\N		\N	\N	\N	particular	\N	2026-01-26 17:34:33.797332	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
125	PRISCILA G BRITO 	\N		\N	\N	\N	unimed	\N	2026-01-26 17:35:19.153295	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
128	SUZETE MAUCH PEREIRA 	\N		1981-06-12	28868300893	\N	unimed	\N	2026-01-26 17:44:52.253048	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
129	GUSTAVO PEIXOTO MARTINS 	\N		1992-04-18	35963071801	\N	particular	\N	2026-01-26 17:46:09.684595	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
74	MAIRA FREY RIFFEL	34991023560		\N			particular	\N	2025-12-12 12:45:22.300385					\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
132	MARINA MARCUZZO DA CRUZ 	34991023560		\N	\N	\N	unimed	\N	2026-01-26 18:15:57.785258	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
133	PEDRO GARCIA PALMA FIGUEIREDO	34991023560		\N	\N	\N	particular	\N	2026-01-26 18:17:04.890922	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
134	EVA GOMES 	\N		\N	\N	\N	unimed	\N	2026-01-26 18:26:45.137199	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
136	PRISCILA PACHIONE 	\N		\N	\N	\N	retorno	\N	2026-01-26 18:27:56.021604	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
137	OLIVIA PACHIONE 	\N		\N	\N	\N	retorno	\N	2026-01-26 18:28:18.073965	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
138	OTAVIO PACHIONE 	\N		\N	\N	\N	unimed	\N	2026-01-26 18:28:54.102638	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
139	ANTONIO BORGES 	\N		\N	\N	\N	retorno	\N	2026-01-26 18:29:20.410514	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
140	CLAUDIO INNOCENTE 	\N		\N	\N	\N	particular	\N	2026-01-26 18:29:41.292405	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
131	FABIANO GALVAO 	34991023560		\N	\N	\N	particular	\N	2026-01-26 18:15:23.642534	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
141	LUIS CARLOS STABILE 	\N		\N	\N	\N	retorno	\N	2026-01-26 18:30:56.204653	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
135	Antonio Cirne Salgado			\N			unimed	\N	2026-01-26 18:27:22.923658					\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
106	VALDINEI MARCOS			\N			retorno	\N	2026-01-21 14:47:56.457706					\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
95	MARIA EUGENIA BORGES CONCEIÇAO			\N			particular	\N	2025-12-16 13:25:30.515476					\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
99	ROSELI GALVANI	16999941774		1953-04-13	00722362803	AV HERACLITO FONTOURA SOBRAL PINTO 551 CASA 49	particular	\N	2026-01-19 17:24:07.016229					\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
105	LUCIANA FINOTO MELO			\N			particular	\N	2026-01-21 14:46:46.764808					\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
103	ALSONIA DE ANDRADE BARBOSA.			\N			particular	\N	2026-01-21 13:09:54.885096					\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
93	MARCIO CUSTODIO DA SILVA	16997981350		1965-01-04			particular	\N	2025-12-15 13:38:20.415744					\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
127	CAMILA CAPARROTI DAL PICOLO ROTIROTI			1982-08-20	30512286809		Particular	\N	2026-01-26 17:43:51.948063					\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
142	DEIVED DOUGLAS GUARNIERI	\N		\N	\N	\N	retorno	\N	2026-01-26 18:31:26.757882	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
143	CIBELE	\N		\N	\N	\N	particular	\N	2026-01-26 18:34:52.913341	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
145	DENISE BALAN 	\N		\N	\N	\N	particular	\N	2026-01-26 18:36:13.330388	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
144	ALVARO GARBINI	\N		\N	\N	\N	particular	\N	2026-01-26 18:35:46.278768	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
126	ANTONIO JACINTHO GUIMARAES 	\N		1975-02-16	09165115880	\N	unimed	\N	2026-01-26 17:40:22.596545	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
146	FELIPE  RUSSO 	16996100593		\N	\N	\N	particular	\N	2026-02-02 13:22:34.299166	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
147	FELIPE  RUSSO 	16996100593		1989-04-12	\N	\N	particular	\N	2026-02-02 13:37:07.415959	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
148	EUCLIDES BERNARDES 	\N		\N	\N	\N	particular	\N	2026-02-02 13:37:55.211492	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
149	RAFAELA MAGNANI DINAMARCO.	16992553560		2010-03-22	55722763837	\N	unimed	\N	2026-02-02 13:39:17.793137	\N	TAISA	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
150	MARCIO JUNIOR 	\N		\N	\N	\N	particular	\N	2026-02-02 13:39:37.388873	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
152	JOICE AP QUINTINO 	\N		\N	\N	\N	particular	\N	2026-02-02 13:40:24.55962	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
155	ADIMARIS GABRIELA RONCADA	\N		\N	\N	\N	particular	\N	2026-02-02 13:45:43.049505	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
197	HELENA ABUD 	\N		\N	\N	\N	particular	\N	2026-02-06 11:41:26.332315	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
157	VICTOR GASPARINI 	\N		\N	\N	\N	particular	\N	2026-02-02 13:47:49.798486	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
158	LUIZ GUSTAVO BACELAR	\N		\N	\N	\N	particular	\N	2026-02-02 13:48:22.959162	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
198	HUGO FRONZAGLIA	\N		\N	\N	\N	particular	\N	2026-02-06 11:42:00.231672	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
151	JOSE RUBENS FURTADO 	\N	\N	1954-05-27	74516884887	\N	particular	pai da kk do rene	2026-02-02 13:39:54.949352	RIBEIRAO PRETO 	\N	\N	\N	SP 	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
159	CAROLINA NAKANO FURTADO STRANG	\N		\N	\N	\N	particular	\N	2026-02-02 14:48:50.314736	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
153	CAIO AUGUSTO 	\N		\N	\N	\N	retorno	\N	2026-02-02 13:41:03.204653	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
156	JULIANA SANTANA 		\N	1983-08-25	31979559864	RUA IRENE TONIOLE DOMENCHI 80 AP 107 	Particular	\N	2026-02-02 13:46:22.462759	RIBEIRAO PRETO 	\N	\N	\N	SP	\N	f	/static/uploads/photos/patient_156_5804a1095ddf47839a36e1048c2832de.jpg	\N	f	\N	\N	\N	\N	\N	\N
175	CLAUDIA SCHOLDEN		\N	\N			particular	\N	2026-02-04 12:00:19.406686					\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
118	MARCO AURELIO BERNARDO	16991555181		1982-03-25	30505971860	AV APARECIDO SAVEGNAGO 200 AP 123 	particular	\N	2026-01-22 14:25:48.621414					\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
161	SABRINA PAVAN VANZO BELEZA	\N		\N	\N	\N	unimed	\N	2026-02-03 11:20:38.010312	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
162	SOLANGE RODRIGUES BARBOSA 	\N		\N	\N	\N	particular	\N	2026-02-03 11:29:05.773514	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
163	LAURA DE CACERES SOUZA 	\N		\N	\N	\N	unimed	\N	2026-02-03 11:30:14.746341	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
164	DIEGO SANTOS 	\N		\N	\N	\N	particular	\N	2026-02-03 11:30:30.952805	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
165	MICHELE SERANTOLA 	\N		\N	\N	\N	particular	\N	2026-02-03 11:30:57.083017	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
166	GUILHERME OLIVEIRA 	\N		\N	\N	\N	particular	\N	2026-02-03 11:31:19.409929	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
167	ENZO	\N		\N	\N	\N	unimed	\N	2026-02-03 11:31:48.679304	\N	ADRIENE	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
168	NICOLAS NEGRI PEREIRA	\N		\N	\N	\N	particular	\N	2026-02-03 12:53:39.655021	\N	\N	\N	\N	\N	\N	f	/static/uploads/photos/patient_168_accd3b46aa0647eb96e8c94fd645d454.jpg	\N	f	\N	\N	\N	\N	\N	\N
169	IRINEU JULIAO JUNIOR	\N		\N	\N	\N	unimed	\N	2026-02-03 14:04:28.002438	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
170	CARLOS ALBERTO TROVAO 	\N		\N	\N	\N	particular	\N	2026-02-03 19:51:22.078883	\N	\N	\N	\N	\N	\N	f	/static/uploads/photos/patient_170_7299017a54f6458b874f35f61bcc7049.jpg	\N	f	\N	\N	\N	\N	\N	\N
173	PEDRO DOMENCIANO 	\N		\N	\N	\N	particular	\N	2026-02-04 11:54:46.857957	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
174	RENATO VILELLA	\N		\N	\N	\N	particular	\N	2026-02-04 11:55:06.704806	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
171	ALEXANDRE VINICIUS DA SILVA PEREIRA 	\N	\N	\N	\N	\N	particular	\N	2026-02-04 11:54:02.571735	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
200	GABRIEL DANEZZI 	\N		\N	\N	\N	particular	\N	2026-02-09 12:49:17.946176	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
172	JOSE MAURICIO AGUIAR JUNIOR 	\N	\N	\N	\N	\N	particular	\N	2026-02-04 11:54:24.148	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
182	ALESSANDRA RIPAMONTE			\N			particular	\N	2026-02-05 12:19:12.858924					\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
176	MATHEUS PELLA 	\N		\N	\N	\N	particular	\N	2026-02-04 19:56:06.716907	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
177	FRANCISCO CHIARELLO FERREIRA 	\N		\N	\N	\N	unimed	\N	2026-02-05 12:14:48.514007	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
178	FRANCISCO ANTONIO	\N		\N	\N	\N	particular	\N	2026-02-05 12:17:21.77307	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
181	GUILHERMINA RIPAMONTE 	\N		\N	\N	\N	unimed	\N	2026-02-05 12:18:46.33397	\N	ALESSANDRA RIPAMONTE	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
183	EMILSON JANUARIO	\N		\N	\N	\N	particular	\N	2026-02-05 12:19:30.587085	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
184	RENAN ANTUNES CONTE 	\N		\N	\N	\N	particular	\N	2026-02-05 12:21:15.855034	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
185	OTAVIO AZEVEDO 	\N		\N	\N	\N	particular	\N	2026-02-05 12:21:41.377585	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
186	OLIVIA AZEVEDO 	\N		\N	\N	\N	particular	\N	2026-02-05 12:21:59.404581	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
199	CLEVER ANGELO DE SOUZA 			\N	\N	\N	Particular	\N	2026-02-09 12:33:54.493055	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
179	VANDERLENA LOT MARTINS	\N	\N	\N	\N	\N	particular	\N	2026-02-05 12:17:46.491855	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
188	SUZETE MAUCH PEREIRA 			1981-06-12	28868300893	\N	Particular	\N	2026-02-05 12:22:44.166292	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
201	LUIS PAULO NASSIF FRANCISCO 	\N		\N	\N	\N	particular	\N	2026-02-09 14:11:07.040287	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
187	DIOGO ARROYO	\N	\N	2009-03-25	\N	\N	particular	\N	2026-02-05 12:22:22.511441	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
189	DENIS CRISTIANO JORA 	\N		\N	\N	\N	particular	\N	2026-02-06 11:24:08.055373	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
190	JONAS RICARDO 	\N		\N	\N	\N	particular	\N	2026-02-06 11:34:53.109719	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
191	NARIELLA MILHARI	\N		\N	\N	\N	particular	\N	2026-02-06 11:35:13.38801	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
192	ANTONIO BORGES 	\N		\N	\N	\N	retorno	\N	2026-02-06 11:35:39.560932	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
193	OTAVIO PACHIONE 	\N		\N	\N	\N	unimed	\N	2026-02-06 11:36:29.35875	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
194	JOSE MATHEUS 	\N		\N	\N	\N	particular	\N	2026-02-06 11:38:04.234185	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
195	FABIANA AZEVEDO 	\N		\N	\N	\N	particular	\N	2026-02-06 11:38:27.83288	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
196	ESDRAS SILVA 	\N		\N	\N	\N	particular	\N	2026-02-06 11:39:42.222855	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
202	LUIS PAULO NASSIF FRANCISCO 	\N		\N	\N	\N	particular	\N	2026-02-09 14:11:07.716624	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
203	CARLOS ROBERTO BUENO JUNIOR	\N		\N	\N	\N	particular	\N	2026-02-09 14:11:30.401143	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
204	ENILSON JANUARIO	\N		\N	\N	\N	particular	\N	2026-02-09 17:23:11.984611	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
205	MARCIO SAULO DE MELLO MARTINS JR	\N		\N	\N	\N	particular	\N	2026-02-09 19:08:13.27871	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
206	MARCELO MAMED ABDALLA 	\N		\N	\N	\N	particular	\N	2026-02-09 19:08:59.669294	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
207	RAFAEL NOGUEIRA 	\N		\N	\N	\N	particular	\N	2026-02-10 12:17:43.8871	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
208	YURI FIRMINO	\N		\N	\N	\N	particular	\N	2026-02-10 12:18:12.586591	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
209	CLAYTON SALLES	\N		\N	\N	\N	particular	\N	2026-02-10 12:21:29.890594	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
210	BRUNO MULATO 	\N		\N	\N	\N	particular	\N	2026-02-10 12:21:51.107633	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
212	CARMEN SILVA 	\N		\N	\N	\N	particular	\N	2026-02-10 12:22:54.557131	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
211	ROBERTO MARTINS	\N		\N	\N	\N	particular	\N	2026-02-10 12:22:39.001225	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
213	RAFAEL CARIOLA 	\N		\N	\N	\N	unimed	\N	2026-02-11 12:06:13.806639	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
214	OTAVIO PACHIONE 			\N	\N	\N	Particular	\N	2026-02-11 12:07:04.55985	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
215	FERNANDO HENRIQUE MARQEUS DE VICENTE 	\N		\N	\N	\N	retorno	\N	2026-02-11 12:08:08.162527	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
217	MILTON CARLOS C DE ALMEIDA PRADO	\N		\N	\N	\N	unimed	\N	2026-02-11 12:08:59.183259	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
218	MARGARIDA SECCHES 	\N		\N	\N	\N	particular	\N	2026-02-11 12:09:20.097477	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
221	JULIA CALSAROLI 	\N		\N	\N	\N	particular	\N	2026-02-11 12:10:29.862351	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
222	ROXANA 	\N		\N	\N	\N	particular	\N	2026-02-11 12:10:47.683328	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
216	HUGO CESAR DOJAS 	\N	\N	1994-01-11	\N	\N	unimed	\N	2026-02-11 12:08:32.109203	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
224	MARIA ISABEL BIAGI DENADAI	16992898929		\N			Particular	\N	2026-02-11 12:11:56.062385					\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
180	LILIANA CRUZ BIAGI SAID			\N			particular	\N	2026-02-05 12:18:09.613849					\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
160	MANUELA NEVES BORTOLO	16991160484		2014-10-08			particular	\N	2026-02-02 20:06:27.840029					\N	\N	f	/static/uploads/photos/patient_160_2aec2aac5017496d8b5700381e0024be.jpg	\N	f	\N	\N	\N	\N	\N	\N
220	JOSEMAR VANZO			\N			particular	\N	2026-02-11 12:10:07.264678					\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
274	NEUZA MARIA REIS DE ALMEIDA 	11999637276	\N	1947-11-17	05477134879	RUA ARNALDO VICTALIAN 1000 APT 34 BLOCO A 	particular	\N	2026-02-24 19:43:37.164454	RIBEIRAO PRETO 	\N	\N	\N	SP 	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
278	MARCIO LUIS MARTINS 	35988340857		1981-08-07	71429093668	\N	particular	\N	2026-02-25 19:07:08.106226	SAO SEBASTIAO PARAIZO	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
226	LUIZA ARROYO DE ALMEIDA PRADO	\N	\N	\N	\N	\N	Particular	\N	2026-02-11 13:58:40.199856	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
279	LUCCA TORRANO FREDERICO CORREA 	\N		\N	\N	\N	particular	\N	2026-02-25 20:01:12.018257	\N	\N	\N	\N	\N	\N	f	/static/uploads/photos/patient_279_3b8a101905a34bb586bf45fe2aac4c64.jpg	\N	f	\N	\N	\N	\N	\N	\N
223	GUILHERME MACHADO CAVALIERI 	\N	\N	\N	39805820866	\N	Particular	\N	2026-02-11 12:11:17.762292	\N	\N	\N	\N	\N	\N	t	/static/uploads/photos/patient_223_fd592fd80e414618a355cc5b97922b55.jpg	\N	f	\N	\N	\N	\N	\N	\N
227	ALEX AP MEDEIROS 	\N		\N	\N	\N	unimed	\N	2026-02-11 20:34:37.468987	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
230	GUILHERME 	\N		\N	\N	\N	particular	\N	2026-02-11 20:36:11.030953	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
231	ROSSI	\N		\N	\N	\N	particular	\N	2026-02-11 20:37:10.288621	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
232	LAURA MINTO 	\N		\N	\N	\N	particular	\N	2026-02-11 20:37:43.34547	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
233	OSVALDO OSSANO 	\N		\N	\N	\N	particular	\N	2026-02-11 20:38:24.96778	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
234	SABRINA PELOSO	\N		\N	\N	\N	particular	\N	2026-02-11 20:39:13.140636	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
236	MATHEUS PELLA 	\N		\N	\N	\N	particular	\N	2026-02-11 20:40:20.88938	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
228	PEDRO SIMATI	\N	\N	\N	\N	\N	particular	\N	2026-02-11 20:35:00.657127	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
235	FERNANDO MORETTO	\N	\N	\N	\N	\N	particular	\N	2026-02-11 20:39:57.769898	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
237	ROBERVAL CARVALHO JUNIOR.	\N	\N	\N	\N	\N	particular	\N	2026-02-12 19:01:43.630307	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
240	ROSANA FARIA 	\N		\N	\N	\N	particular	\N	2026-02-13 11:43:05.998306	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
241	RAFAEL NASCIMENTO CARIOLA 	\N		\N	\N	\N	unimed	\N	2026-02-13 11:43:28.703516	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
242	JOSE RICARDO MINATEL	\N		\N	\N	\N	particular	\N	2026-02-13 11:44:45.00577	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
244	JOVITA MADALENA ALVES MORENO	\N		\N	\N	\N	particular	\N	2026-02-13 11:47:04.026676	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
238	FRANCISCO CHIARELLO FERREIRA 	\N	\N	\N	\N	\N	unimed	\N	2026-02-13 11:42:06.72428	\N				\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
245	NATALIA LETICIA TEIXEIRA ALVES 	\N		\N	\N	\N	unimed	\N	2026-02-13 18:09:20.923996	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
247	ALCIDIA DE CASSIA 	\N		\N	\N	\N	particular	\N	2026-02-13 18:12:01.91213	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
248	MARTA RODRIGUES MAFEIS 	\N		\N	\N	\N	particular	\N	2026-02-13 18:15:51.533288	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
250	ROSANO SOUZA 	\N		\N	\N	\N	particular	\N	2026-02-13 18:16:33.294327	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
251	JULIANNA 	\N		\N	\N	\N	particular	\N	2026-02-13 18:16:46.830392	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
252	GUSTAVO MAGALAHES 	\N		\N	\N	\N	retorno	\N	2026-02-13 18:17:06.409306	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
253	JOSEANE	\N		\N	\N	\N	particular	\N	2026-02-13 18:18:11.217036	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
254	SERGIO NUNES	\N		\N	\N	\N	particular	\N	2026-02-13 18:18:53.948491	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
256	JOSE FONSECA NETO	\N		\N	\N	\N	particular	\N	2026-02-13 18:19:35.870988	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
257	MAURO COLICCHIO	\N		\N	\N	\N	particular	\N	2026-02-13 18:20:18.994709	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
258	GUILHERME SANTOS 	\N		\N	\N	\N	particular	\N	2026-02-13 18:20:37.88575	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
261	GIOVANNA FIORI	\N		\N	\N	\N	particular	\N	2026-02-13 18:21:54.069427	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
262	FERNANDO ANTONIO MAURO PESSOA 	\N		\N	\N	\N	particular	\N	2026-02-13 18:23:15.779558	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
280	LENNON FLAVIO	\N		\N	\N	\N	particular	\N	2026-02-26 11:27:30.322184	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
243	JOSE CARLOS FORTES GUIMARAES 	\N		\N	\N	\N	particular	tcc	2026-02-13 11:45:55.624026	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
246	LUIZ FERNANDO 	\N		\N	\N	\N	particular	\N	2026-02-13 18:09:44.707153	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
249	WALTER S JUNIOR 	\N		\N	\N	\N	particular	\N	2026-02-13 18:16:13.279279	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
263	LUIZ CARLOS PHEBER	\N		\N	\N	\N	particular	\N	2026-02-19 13:34:43.693404	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
255	LUIS CARLOS 	\N		\N	\N	\N	particular	\N	2026-02-13 18:19:20.111032	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
260	RENAN PEIXOTO 	\N		\N	\N	\N	particular	\N	2026-02-13 18:21:37.002548	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
281	PEDRO GARCIA FERRAO 	\N		\N	\N	\N	particular	\N	2026-02-26 11:27:49.926664	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
264	MARCILENE APARECIDA GONÇALVES 	\N		\N	\N	\N	particular	\N	2026-02-23 14:22:12.599206	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
239	ISABELLA SALGADO JUCATELLI			\N			particular	\N	2026-02-13 11:42:46.001947					\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
265	CARLOS ROBERTO MARQUES JUNIOR 	\N		\N	\N	\N	particular	\N	2026-02-24 19:36:52.463179	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
266	LUIZ ALEXANDRE PANINI 	\N		\N	\N	\N	particular	\N	2026-02-24 19:37:53.861006	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
269	DENISE BALAN 	\N		\N	\N	\N	particular	\N	2026-02-24 19:39:43.766282	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
270	BRUNA TUCCI SANTIAGO	\N		\N	\N	\N	particular	\N	2026-02-24 19:40:10.260259	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
271	WILHIAN MONASSI	\N		\N	\N	\N	particular	\N	2026-02-24 19:40:38.646112	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
272	WILHIAN MONASSI	\N		\N	\N	\N	particular	\N	2026-02-24 19:40:38.655681	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
273	MELISSA SOARES 	\N		\N	\N	\N	particular	\N	2026-02-24 19:43:02.885602	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
275	VERA GARCIA	\N		\N	\N	\N	particular	\N	2026-02-24 19:44:39.126422	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
276	RAFAEL VALERIO  ARANHA	\N		\N	\N	\N	retorno	\N	2026-02-24 19:45:30.27045	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
268	MARIANA FRANÇA BAYEUX POTENZA 	\N	\N	\N	\N	\N	particular	\N	2026-02-24 19:38:54.26007	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
267	GABRIEL BAYAX POTENZA 	\N	\N	\N	\N	\N	particular	\N	2026-02-24 19:38:32.914353	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
277	DENISE BALAN 	\N		\N	\N	\N	particular	\N	2026-02-25 17:44:15.044548	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
282	LUANA BOSCHETI	\N		\N	\N	\N	particular	\N	2026-02-26 11:28:13.123455	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
284	RAFAEL COLICCHIO	\N		\N	\N	\N	particular	\N	2026-02-26 11:29:09.87203	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
285	SILVANA COLICCHIO	\N		\N	\N	\N	particular	\N	2026-02-26 11:29:34.985251	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
287	APARECIDA DONIZETE 	\N		\N	\N	\N	particular	\N	2026-02-26 11:30:48.85736	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
288	MARIA VICTORIA 	\N		\N	\N	\N	particular	\N	2026-02-26 11:31:09.4202	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
293	DOUGLAS BRAGA TORRES BLANCA 	\N		\N	\N	\N	particular	\N	2026-02-27 13:20:48.80022	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
289	GUSTAVO PASCHOAL	\N	\N	\N	\N	\N	particular	\N	2026-02-26 11:31:46.451496	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
290	GABRIELA BENEDINE 	\N		\N	\N	\N	particular	\N	2026-02-26 11:32:47.162152	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
291	DENISE BALDAN	\N		1980-01-07	28673053811	\N	particular	\N	2026-02-26 13:01:26.141292	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
294	JOAQUIM FOLIETE SANTOS 	\N		\N	\N	\N	particular	\N	2026-02-27 13:21:10.223202	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
292	MARCELO DANILO ZANFRILLE 	\N		\N	33662136805	\N	particular	desenho conservador \nirmao fez e gostou muito\n\ncalvicie muito extensa	2026-02-26 13:15:01.070962	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
283	ROSANA ALVES 	\N		\N	\N	\N	particular	\N	2026-02-26 11:28:38.377073	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
295	THAISA MARIA VELLASCO QUEIROZ PIMENTA. 	\N		\N	\N	\N	particular	\N	2026-02-27 13:21:45.011001	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
298	CRISLAINE JAMARINO 	\N		\N	\N	\N	particular	\N	2026-02-27 13:23:12.567318	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
296	ANDERSON SILVEIRA 	\N		\N	\N	\N	retorno	\N	2026-02-27 13:22:28.620344	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
297	MARCIA NASSUR 			\N	\N	\N	Particular	\N	2026-02-27 13:22:51.298532	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
299	CLAUDIO INNOCENTE 	\N		\N	\N	\N	particular	\N	2026-02-27 17:09:38.417919	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
301	SANDRA MARCIA FERRAO ZAPOLLA	\N		\N	\N	\N	particular	\N	2026-02-27 17:11:47.338416	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
302	ILLAN SALES GALVAO DE FIGUEIREDO	\N		\N	\N	\N	particular	\N	2026-02-27 17:13:12.18119	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
303	FABIANO GALVAO 	34991023560		\N	\N	\N	particular	\N	2026-02-27 17:16:14.120959	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
304	GUILHERME OLIVEIRA 	\N		\N	\N	\N	particular	\N	2026-02-27 17:17:13.020539	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
305	FATIMA SOLANGE COSTA CAMPOS 	\N		\N	\N	\N	particular	\N	2026-02-27 17:17:50.709579	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
306	CARLOS ALBERTO TROVAO 	\N		\N	\N	\N	particular	\N	2026-02-27 17:18:10.798809	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
286	DANIEL DE JESUS BONFIM 	\N		\N	\N	\N	particular	\N	2026-02-26 11:30:24.475041	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
225	GISELE CRISTINA DE ARAUJO 		\N	1986-12-19			particular	\N	2026-02-11 12:57:04.407196					\N	\N	f	/static/uploads/photos/patient_225_f6996528302d4732bbc97fc869f5c3d3.jpg	\N	f	\N	\N	\N	\N	\N	\N
259	DANIELE BIAGI			\N			particular	\N	2026-02-13 18:21:21.713489					\N	\N	f	\N	3	t	2026-03-09 13:15:16.426775	\N	\N	\N	\N	\N
340	ADILSON HADDAD	16997700261	\N	\N	\N	\N	particular	\N	2026-03-04 12:07:59.361235	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
300	LUCAS AUGUSTO	\N		\N	\N	\N	particular	\N	2026-02-27 17:11:00.152045	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
309	FELIPE RUSSO 	\N		\N	\N	\N	particular	\N	2026-03-02 11:18:20.315214	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
312	JOAO VITOR 	\N		\N	\N	\N	particular	\N	2026-03-02 11:19:37.93711	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
316	SUZETE MAUCH PEREIRA 	\N		1981-06-12	28868300893	\N	unimed	\N	2026-03-02 11:22:50.577839	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
317	CACILDA SANTIAGO 	\N		\N	\N	\N	particular	\N	2026-03-02 11:34:32.338545	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
319	JULIANA SANTANA 	\N		1983-08-25	31979559864	RUA IRENE TONIOLE DOMENCHI 80 AP 107 	Particular	\N	2026-03-02 11:35:39.936096	RIBEIRAO PRETO 	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
354	VALERIA GUAPO MACHADO 	\N		\N	\N	\N	particular	\N	2026-03-04 17:04:27.666316	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
308	EMILIO CURY	\N		\N	\N	\N	particular	\N	2026-03-02 11:07:10.10867	\N	\N	\N	\N	\N	\N	f	\N	3	t	2026-03-02 12:32:32.258	\N	\N	\N	\N	\N
311	JOAO VICTOR SOMERA 	16992954600	\N	1984-06-25	33058230893	RUA JOSE ANDREOLI 322 	unimed	\N	2026-03-02 11:19:14.76905	RIBEIRAO PRETO 	\N	\N	\N	SP 	14026130	f	\N	\N	f	\N	\N	\N	\N	\N	\N
310	RAFAEL LUIZ SPINA	\N		\N	\N	\N	particular	\N	2026-03-02 11:18:47.265683	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
355	MARIA CRISTINA MAFUD 	\N		\N	\N	\N	particular	\N	2026-03-04 17:05:27.663957	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
359	LUCAS DANIEL 	\N		\N	\N	\N	particular	\N	2026-03-05 11:59:23.056578	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
351	ROSEMAR DE SOUZA SILVA			\N	\N	\N	Particular	\N	2026-03-04 12:24:01.655591	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
335	BRUNA RODRIGUES 		\N	2011-12-27	46024424809	\N	Particular	\N	2026-03-03 18:46:35.738949	SAO SIMAO 	\N	\N	\N	\N	\N	f	/static/uploads/photos/patient_335_e37f7c7e1815471b80add4fc3197c3ea.jpg	\N	f	\N	\N	\N	\N	\N	\N
314	ALEXANDRA CRISTINA BARBOSA 	\N		\N	\N	\N	particular	\N	2026-03-02 11:20:19.273165	\N	\N	\N	\N	\N	\N	f	\N	3	t	2026-03-02 14:05:39.068116	\N	\N	\N	\N	\N
313	JOAO VITOR JARDIM DA SILVA 	\N	\N	1992-05-26	01811340636	RUA JOSE BACHETE 458 	Particular	\N	2026-03-02 11:19:42.749023	SERTAOZINHO 	\N	\N	\N	SP 	\N	t	/static/uploads/photos/patient_313_b5e6db668f7e49388557c89c64a0960e.jpg	\N	f	\N	\N	\N	\N	\N	\N
315	POLIANA MODA 	\N		\N	\N	\N	particular	\N	2026-03-02 11:21:37.11973	\N	\N	\N	\N	\N	\N	f	\N	3	t	2026-03-02 18:05:23.092031	\N	\N	\N	\N	\N
320	ANA LIGIA SANTOS DE OLIVEIRA 	\N		1987-06-19	32294740823	\N	particular	\N	2026-03-02 18:07:11.846346	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
318	WILHIAN KLEBER 	\N		\N	\N	\N	particular	paciente feliz mas gostaria de auemntar  adensidade do topete posterior e do escalpe que nem foi colocado\nesta em uso de minzodil com melhora geral do afinamento\nentro com finasterida	2026-03-02 11:35:05.255792	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
323	ANDREIA PINTO 	\N		\N	\N	\N	particular	\N	2026-03-03 11:11:24.406264	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
325	EDUARDO HENRIQUE GOMES 	\N		\N	\N	\N	particular	\N	2026-03-03 11:12:11.376638	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
327	MARINA CILINO	\N		\N	\N	\N	retorno	\N	2026-03-03 11:13:24.3888	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
328	MARCILENE APARECIDA GONÇALVES 	\N		\N	\N	\N	particular	\N	2026-03-03 11:54:58.537036	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
329	JANDIMILIA	\N		\N	\N	\N	particular	\N	2026-03-03 11:56:41.847956	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
336	luciana pimenta mattos			\N			particular	\N	2026-03-04 11:31:55.43573					\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
321	BRANCA MEIRELLES 	16992017072	\N	1985-11-13	05226096941	\N	unimed	\N	2026-03-03 11:10:30.769317	pradopolis 	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
331	MARISSON DONLEY WIRGUES	\N		1972-08-20	25237680895	RUA RUBEM ALOISIO 	particular	\N	2026-03-03 12:08:01.857141	RIBEIRAO PRETO	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
337	RENATA CHIARELLO PEREIRA 	16997770052		0957-08-04	\N	adolfo serra 1725 - casa 7	particular	\N	2026-03-04 12:05:54.89096	ribeirao preto 	\N	\N	\N	\N	\N	f	/static/uploads/photos/patient_337_2c9c7dc51eef453fb810268de4aac4d7.jpg	\N	f	\N	\N	\N	\N	\N	\N
339	PEDRO DOMENCIANO 	\N		\N	\N	\N	particular	\N	2026-03-04 12:07:09.115499	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
326	JULIA FONTANETTI		\N	1998-11-16	\N	R DR. JULIO XAVIER 501	Particular	\N	2026-03-03 11:12:49.707904	CRAVINHOS 	\N	\N	\N	SP	\N	f	/static/uploads/photos/patient_326_3602cdced0a240daa3595e5663b2f67a.jpg	\N	f	\N	\N	\N	\N	\N	\N
333	BRUNA GABRIELA MONTAGNANI	\N		\N	\N	\N	unimed	\N	2026-03-03 12:57:51.226905	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
322	MARISSON DONLEY WIEGUES	\N	\N	\N	\N	\N	Particular	mae do marcelo da barao	2026-03-03 11:10:56.782293	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
324	ISADORA GOMES 	\N	\N	2005-03-09	39837402865	AV JOSE PEREIRA GOMES 183 	Particular	\N	2026-03-03 11:11:40.192876	\N	\N	\N	\N	\N	\N	f	/static/uploads/photos/patient_324_7473663f59dd47ed8047ab4250a2e5db.jpg	\N	f	\N	\N	\N	\N	\N	\N
334	RAFAEL FURTADO CARLOS DE OLIVEIRA 	\N		\N	\N	\N	particular	\N	2026-03-03 17:35:54.566084	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
344	JULIANA PRADELA	\N		\N	\N	\N	particular	\N	2026-03-04 12:11:35.774538	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
330	SARA SERAFIN LIMA		\N	2006-08-04	\N	\N	Particular	\N	2026-03-03 11:58:28.848546	ribeirao preto	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
348	ANA LUISA TENORI	\N		\N	\N	\N	particular	\N	2026-03-04 12:14:45.327769	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
349	ANTONIA GOIS DA SILVA DE MORAIS	\N		\N	\N	\N	particular	\N	2026-03-04 12:18:06.61528	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
350	DANI 	16997319949		\N	\N	\N	particular	\N	2026-03-04 12:23:44.267526	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
352	IVANI CARLA OMETTO	16991909355		\N	\N	\N	particular	\N	2026-03-04 12:24:23.062664	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
353	THAIS 	16993728585		\N	\N	\N	particular	\N	2026-03-04 12:24:46.778056	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
229	CAMILA UBIDA	1698876747		\N			Particular	\N	2026-02-11 20:35:31.3712					\N	\N	f	/static/uploads/photos/patient_229_1845d96cbee24e30ac01dd098f30a7f8.jpg	\N	f	\N	\N	\N	\N	\N	\N
338	MARILIA DE CAMARGO BIASI 			\N	\N	\N	Particular	\N	2026-03-04 12:06:46.185468	\N	\N	\N	\N	\N	\N	f	/static/uploads/photos/patient_338_9ba50e8199674619abb4d62bed1540e3.jpg	\N	f	\N	\N	\N	\N	\N	\N
342	DORAMA MODA 	16991936339	\N	1966-09-20	\N	\N	particular	\N	2026-03-04 12:10:25.058754	\N	\N	\N	\N	\N	\N	f	\N	2	t	2026-03-04 17:38:32.548433	\N	\N	\N	\N	\N
343	GUILHERME GRIFFO	\N		\N	\N	\N	particular	\N	2026-03-04 12:11:15.145625	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
341	ELIANE HADDAD	16997660261	\N	1963-09-12	08798612824	\N	particular	\N	2026-03-04 12:08:23.006666	\N	\N	\N	\N	\N	\N	f	\N	2	t	2026-03-04 14:46:14.441562	\N	\N	\N	\N	\N
345	EUCLIDES BERNARDES 	\N		\N	\N	\N	particular	\N	2026-03-04 12:11:57.292628	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
356	MARIA DARCY TEIXEIRA A. SIQUEIRA	\N		\N	\N	\N	particular	\N	2026-03-04 19:41:54.812479	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
346	WALTER BALBI	\N		\N	\N	\N	particular	\N	2026-03-04 12:12:20.692372	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
347	CIBELE SIQUEIRA 			\N	\N	\N	Particular	\N	2026-03-04 12:12:39.617346	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
357	GERLAINE 	8892575888		\N	\N	\N	particular	\N	2026-03-05 11:30:38.332798	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
358	NEUZA MARIA REIS DE ALMEIDA 			1947-11-17	05477134879	\N	Particular	\N	2026-03-05 11:51:12.145731	\N	\N	\N	\N	\N	\N	f	/static/uploads/photos/patient_358_83a172ba11bb4a9aa42f4d82b5d32595.jpg	\N	f	\N	\N	\N	\N	\N	\N
362	ANDREA GOMES PINTO 	\N		\N	\N	\N	particular	\N	2026-03-05 12:01:52.901665	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
364	SANDRA 	16997861919		\N	\N	\N	particular	\N	2026-03-05 12:05:51.652099	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
307	ROXANA CAZON ANGELO			\N			particular	\N	2026-02-27 17:41:02.641492					\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
360	CLEBER ROBERTO VIOLIN	\N	\N	\N	\N	\N	particular	\N	2026-03-05 12:00:44.892736	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
372	ANDREIA PINTO 	\N		\N	\N	\N	particular	\N	2026-03-05 14:36:31.130508	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
373	ANDREIA PINTO 	\N		\N	\N	\N	particular	\N	2026-03-05 14:37:31.275005	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
374	SUELI GOTARDI MOITINHO.	16997467027		1962-02-04	09545962852	\N	retorno	\N	2026-03-05 17:27:04.489111	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
366	JOSE SAMUEL 	\N		\N	\N	\N	particular	\N	2026-03-05 12:11:51.511003	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
365	SHAOYAN CHEN	11949939295	\N	\N	\N	RUA CATHARINA PAGLIESI MOBIGLIA 905	UNIMED	\N	2026-03-05 12:06:15.136897	ribeirao preto 	\N	\N	\N	sp 	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
375	MURILO NAZI ARNONI 	\N		\N	\N	\N	unimed	\N	2026-03-06 11:51:25.705328	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
368	ERNANE DONIZETE	\N		\N	\N	\N	particular	\N	2026-03-05 12:13:30.792962	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
369	ADRIANO BRANDAO 	24981825418	\N	1985-03-16	11238039782	\N	particular	\N	2026-03-05 12:13:50.562869	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
367	MARCIUS SIERRO DIAS 		\N	1986-11-30	34431163883	RUA JOAO LASTORIA 249 	Particular	\N	2026-03-05 12:12:40.570899	DESCALÇVADO 	\N	\N	\N	SP 	\N	t	/static/uploads/photos/patient_367_c077cba0c8a94270bd588815836810b6.jpg	\N	f	\N	\N	\N	\N	\N	\N
376	MANUELA NAZINI	\N		\N	\N	\N	particular	\N	2026-03-06 12:11:11.883553	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
363	ANNA KARINA BOLINI			\N			Particular	\N	2026-03-05 12:05:07.425968					\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
332	BRUNO BATAER			\N			particular	\N	2026-03-03 12:56:17.738158					\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
377	FELIPE RANGEL 	16992100804	\N	\N	\N	\N	particular	\N	2026-03-06 12:11:32.88985	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
378	EVILYN MARIA COLANGELO 	\N	\N	\N	\N	\N	Particular	\N	2026-03-06 12:13:02.287297	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
384	CRISLAINE JAMARINO 	\N		\N	\N	\N	particular	\N	2026-03-09 11:42:35.516422	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
386	RAMON WENDLER SILVA 	\N	\N	\N	\N	\N	particular	\N	2026-03-09 11:44:27.988864	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
406	LUIS ALBERTO	\N		\N	\N	\N	particular	\N	2026-03-11 11:49:34.505369	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
407	MARIA EDUARDA VANZO	\N		\N	\N	\N	unimed	\N	2026-03-11 11:51:45.249895	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
379	RENATO CESAR STELLA	\N	\N	\N	\N	\N	particular	\N	2026-03-09 11:35:58.618896	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
380	SILVIO MARTINS JUNIOR 		\N	1992-12-01	41257640807	RUA JAPURA 1751	Particular	\N	2026-03-09 11:37:07.071064	RIBEIRAO PRETO 	\N	\N	\N	SP 	14060620	t	/static/uploads/photos/patient_380_6995451276b94f8fa47c9753880f40d9.jpg	\N	f	\N	\N	\N	\N	\N	\N
381	DENIS GUSTAVO MORENO	\N	\N	\N	\N	\N	particular	\N	2026-03-09 11:40:15.259935	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
409	ANA MARIA BIAGI	\N		\N	\N	\N	particular	\N	2026-03-11 11:57:07.131772	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
410	JOAO PEDRO 	\N		\N	\N	\N	particular	\N	2026-03-11 11:57:57.506596	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
411	RAFAEL DE CARVALHO NOGUEIRA 	16981249625		1983-02-17	22487889837	Rua Newton Estilac Leal 291 AP 3	particular	\N	2026-03-11 12:32:53.143499	Ribeirão Preto	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
402	HENRIQUE CROSIO FILHO	16997924364	\N	\N	18268692634	\N	particular	\N	2026-03-11 11:36:18.876191	\N	\N	\N	\N	\N	\N	t	/static/uploads/photos/patient_402_989ed8bb09944fec91254c2884b39924.jpg	\N	f	\N	\N	\N	\N	\N	\N
383	LUIS GUSTAVO TORRANO CORREA 		\N	1969-06-22	15081448850	RUA LUIS AUGUSTO MACHADO SANTANA 520 CASA 601	Particular	\N	2026-03-09 11:42:13.390786	RIBEIRAO PRETO 	\N	\N	\N	SP 	14100000	t	/static/uploads/photos/patient_383_7e28985ea2344025ab1117bfb74dc338.jpg	\N	f	\N	\N	\N	\N	\N	\N
385	GABRIEL DANEZZI 	\N		\N	\N	\N	particular	\N	2026-03-09 11:43:53.549063	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
387	ISABELLA SUHADOLNIK MAIA BARBOSA 	35998496330	ISASOCMAIA@HOTMAIL.COM	1995-12-31	11503418669	RUA LAZARA MARIA DE OELICEIRA 100 AP 74	UNIMED	\N	2026-03-09 11:44:42.410337	RIBEIRAO PRETO 	\N	\N	\N	SP 	14027025	f	/static/uploads/photos/patient_387_07595037ea3f436eaa5481521907b5cf.jpg	\N	f	\N	\N	\N	\N	\N	\N
388	RAISSA FRANCIELE 	\N		\N	\N	\N	particular	\N	2026-03-10 11:16:49.471411	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
389	EUCLIDES BERNARDES 	\N		\N	\N	\N	particular	\N	2026-03-10 11:17:08.598708	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
391	ALESSANDRA AP BIDO RIBEIRO	\N		\N	\N	\N	unimed	\N	2026-03-10 11:18:38.467316	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
392	DANILO PANTALEAO MARÇAL 	\N		\N	\N	\N	particular	\N	2026-03-10 11:19:02.097973	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
393	ROSANA CASTELLI	\N		\N	\N	\N	particular	\N	2026-03-10 11:19:58.448872	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
394	LUCIENE CASTELLI	\N		\N	\N	\N	particular	\N	2026-03-10 11:20:14.192647	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
397	JULIA CALSAROLI 	\N		\N	\N	\N	particular	\N	2026-03-10 11:21:23.839366	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
382	CAMILA DE BARROS MEIRELLES 	\N	\N	1988-08-12	37972956855	RUA PRAÇA RONE JOAQUIM ALVES 123 AP  800	Particular	\N	2026-03-09 11:41:58.089421	BATATAIS 	\N	\N	\N	SP	14300970	f	/static/uploads/photos/patient_382_319ae093a431427cbb3414c28e610ef4.jpg	1	t	2026-03-10 11:37:41.757957	\N	\N	\N	\N	\N
390	MARIA MARGARETH DENARDI BOSA	17991574989	\N	1963-08-15	05053244820	ALAMEDA PAINEIRA 150	particular	\N	2026-03-10 11:18:11.491605	BEBEDOURO	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
396	ROSANJO SOUZA 	\N		\N	\N	\N	particular	\N	2026-03-10 11:21:03.389704	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
404	MARIA CELIA ZULIAN 	19981398261		\N	\N	\N	Particular	\N	2026-03-11 11:41:58.820847	\N	\N	\N	\N	\N	\N	f	/static/uploads/photos/patient_404_a4ffa8c75170413e80f86b80066339ad.jpg	\N	f	\N	\N	\N	\N	\N	\N
412	ROBERTO AUDE JABALI 	16996391988		1970-05-16	07170208865	\N	particular	\N	2026-03-11 14:24:05.70665	RIBEIRAO PRETO 	MARIANA JABALI 	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
395	CLEITON DIAS 	16981544532		\N	\N	\N	Particular	\N	2026-03-10 11:20:30.540538	\N	\N	\N	\N	\N	\N	t	/static/uploads/photos/patient_395_c41a6e7b21124bea90e98948cbd66778.jpg	\N	f	\N	\N	\N	\N	\N	\N
219	LEANDRO LUIZ DE ARAUJO LIMA ZAPAROLI 			\N			Particular	\N	2026-02-11 12:09:42.344651					\N	\N	f	/static/uploads/photos/patient_219_922c4a61ecd148ea903190745fa6395e.jpg	\N	f	\N	\N	\N	\N	\N	\N
398	FABIO ALEXANDRE CARNEIRO 	\N		\N	\N	\N	particular	\N	2026-03-11 11:33:10.637706	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
401	MILTON BORBA	\N		\N	\N	\N	particular	\N	2026-03-11 11:35:47.747497	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
403	MARINA GARCIA HECK	\N		\N	\N	\N	unimed	\N	2026-03-11 11:37:49.551547	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
399	RICARDO VILELA SAID 	16981271717		\N	\N	\N	Particular	tcc quer fazer long hair	2026-03-11 11:34:00.959571	\N	\N	\N	\N	\N	\N	t	/static/uploads/photos/patient_399_18e940b8b6e54eb9809564d3cb126466.jpg	\N	f	\N	\N	\N	\N	\N	\N
405	VINICIUS ROCHA MARQUES 			\N	\N	\N	Particular	\N	2026-03-11 11:49:19.891076	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
400	GUSTAVO AVILEZ MACRI 	\N	\N	1997-12-05	\N	\N	particular	\N	2026-03-11 11:35:25.051276	\N	\N	\N	\N	\N	\N	t	/static/uploads/photos/patient_400_b7154e322f1f45a991c4fa49efeb7e1e.jpg	\N	f	\N	\N	\N	\N	\N	\N
413	GUSTAVO CASTILHO SOARES	\N		\N	\N	\N	particular	\N	2026-03-11 19:08:58.707856	\N	\N	\N	\N	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N
419	MAYARA MAINA MELO E GUIAO	1691338422		\N	\N	\N	particular	\N	2026-03-12 17:53:18.184553	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
408	LETICIA FABBRI			\N	\N	\N	Particular	\N	2026-03-11 11:52:06.754439	\N	\N	\N	\N	\N	\N	f	/static/uploads/photos/patient_408_204c37894abc4d98b99195a8844fda98.jpg	\N	f	\N	\N	\N	\N	\N	\N
420	APARECIDA DONIZETE BECARI FERREIRA 	16991208711		\N	\N	\N	particular	\N	2026-03-12 18:06:24.682585	\N	\N	\N	\N	\N	\N	f	\N	\N	f	\N	\N	\N	\N	\N	\N
\.


--
-- Data for Name: patient_doctor; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.patient_doctor (id, patient_id, doctor_id, patient_code, created_at) FROM stdin;
1	1	5	1	2025-11-25 18:00:30.019871
2	2	5	2	2025-11-25 18:11:56.891827
3	3	6	1	2025-11-25 18:34:27.167299
4	4	6	2	2025-11-25 18:35:44.494168
5	5	6	3	2025-11-26 11:39:29.314098
6	6	6	4	2025-11-26 12:42:25.550674
7	7	6	5	2025-11-26 12:43:30.881319
8	8	6	6	2025-11-26 12:44:20.906631
9	9	6	7	2025-11-26 12:45:43.512622
10	10	5	3	2025-11-26 18:01:37.837237
11	11	6	8	2025-11-27 12:46:46.44869
12	11	5	4	2025-11-27 14:52:57.776728
14	13	6	9	2025-11-27 17:19:46.335108
15	14	6	10	2025-11-27 17:20:35.087278
16	13	5	5	2025-11-27 17:57:45.488897
17	14	5	6	2025-11-27 17:58:57.412884
18	15	5	7	2025-11-28 12:33:13.115448
19	16	5	8	2025-11-28 15:56:09.835564
20	17	5	9	2025-11-28 19:51:20.306596
21	18	6	11	2025-12-02 12:34:35.171228
22	18	5	10	2025-12-02 12:35:22.076122
23	19	5	11	2025-12-02 12:39:53.769496
24	20	5	12	2025-12-02 12:47:01.723225
25	21	5	13	2025-12-02 12:48:37.216563
26	22	5	14	2025-12-02 12:50:06.69593
27	23	5	15	2025-12-02 12:50:22.35522
28	24	5	16	2025-12-02 12:52:02.578677
29	25	5	17	2025-12-02 12:53:49.71862
30	26	5	18	2025-12-02 13:00:39.286034
31	27	5	19	2025-12-03 12:27:10.361296
32	7	5	20	2025-12-03 12:27:59.342032
33	28	5	21	2025-12-03 12:29:53.846985
34	29	6	12	2025-12-03 12:33:41.550284
35	29	5	22	2025-12-03 12:34:42.513421
36	30	5	23	2025-12-03 12:37:03.859039
37	31	6	13	2025-12-03 12:40:50.033429
38	31	5	24	2025-12-03 12:41:59.270024
39	32	5	25	2025-12-03 12:43:56.085287
40	33	5	26	2025-12-03 18:25:58.487387
41	34	5	27	2025-12-04 13:48:50.282157
42	35	5	28	2025-12-04 18:07:40.675514
43	36	5	29	2025-12-05 12:47:41.94577
44	37	5	30	2025-12-05 12:48:25.82238
45	38	5	31	2025-12-05 12:52:27.75544
46	39	5	32	2025-12-05 13:16:17.667433
47	40	5	33	2025-12-05 17:44:38.959561
48	41	5	34	2025-12-09 15:29:38.369364
49	42	5	35	2025-12-09 15:30:37.427975
50	43	5	36	2025-12-09 15:32:36.807624
51	44	5	37	2025-12-09 15:33:49.903814
52	45	5	38	2025-12-09 15:34:12.201755
53	46	5	39	2025-12-09 15:34:59.201533
54	47	5	40	2025-12-09 15:35:21.755456
55	48	5	41	2025-12-09 17:50:41.687856
56	49	5	42	2025-12-09 18:18:15.337143
57	50	5	43	2025-12-10 15:36:13.755833
58	51	5	44	2025-12-10 15:37:14.110541
59	52	5	45	2025-12-10 15:38:44.927762
60	53	5	46	2025-12-10 15:39:11.576989
61	54	5	47	2025-12-10 15:40:21.371491
62	55	5	48	2025-12-10 15:40:47.76859
63	56	5	49	2025-12-10 15:41:59.011929
64	57	5	50	2025-12-10 18:11:18.287451
65	58	5	51	2025-12-11 11:52:16.294559
66	59	5	52	2025-12-11 11:55:24.642108
67	60	5	53	2025-12-11 13:28:09.882654
68	61	5	54	2025-12-11 13:37:59.451039
69	62	5	55	2025-12-11 14:53:38.678149
70	63	5	56	2025-12-11 17:57:52.82543
71	64	5	57	2025-12-11 18:15:16.091949
72	65	5	58	2025-12-11 19:07:40.196567
73	66	5	59	2025-12-12 12:25:14.605542
74	67	5	60	2025-12-12 12:26:54.628338
75	68	5	61	2025-12-12 12:27:55.257436
76	69	5	62	2025-12-12 12:29:36.595517
77	70	5	63	2025-12-12 12:30:39.663629
78	71	5	64	2025-12-12 12:37:10.79206
79	72	5	65	2025-12-12 12:40:44.927897
80	73	5	66	2025-12-12 12:42:01.574858
81	74	5	67	2025-12-12 12:45:22.474632
82	75	5	68	2025-12-12 18:08:20.914139
83	76	5	69	2025-12-12 18:33:52.179094
84	77	5	70	2025-12-12 18:34:33.261747
85	78	5	71	2025-12-12 18:35:04.155458
86	79	5	72	2025-12-12 18:40:00.152173
87	80	5	73	2025-12-12 18:42:30.737624
88	81	5	74	2025-12-12 19:49:20.723602
89	82	5	75	2025-12-15 12:53:27.045208
90	83	5	76	2025-12-15 12:54:51.276491
91	84	5	77	2025-12-15 13:00:23.47045
92	85	5	78	2025-12-15 13:02:28.482422
93	86	5	79	2025-12-15 13:10:13.10683
94	87	5	80	2025-12-15 13:25:06.404191
95	88	5	81	2025-12-15 13:28:55.11999
96	89	5	82	2025-12-15 13:31:30.018865
97	90	5	83	2025-12-15 13:33:31.867647
98	91	5	84	2025-12-15 13:34:13.179502
99	92	5	85	2025-12-15 13:35:47.366915
100	93	5	86	2025-12-15 13:38:20.591047
101	94	5	87	2025-12-16 13:23:12.607379
102	95	5	88	2025-12-16 13:25:30.720277
103	96	5	89	2025-12-16 13:27:25.535932
104	97	5	90	2026-01-19 15:36:28.539635
105	98	5	91	2026-01-19 17:16:54.232964
106	99	5	92	2026-01-19 17:24:07.196347
107	100	5	93	2026-01-19 17:36:24.193986
108	101	5	94	2026-01-21 13:00:05.768255
109	102	5	95	2026-01-21 13:08:18.088197
110	103	5	96	2026-01-21 13:09:55.072238
111	104	5	97	2026-01-21 14:19:36.672201
112	105	5	98	2026-01-21 14:46:46.950508
113	106	5	99	2026-01-21 14:47:56.636423
114	107	5	100	2026-01-21 14:48:39.079035
115	108	5	101	2026-01-21 14:49:10.877992
116	109	5	102	2026-01-21 14:49:37.28239
117	110	5	103	2026-01-21 14:51:04.413502
118	111	5	104	2026-01-21 14:51:30.266504
119	112	5	105	2026-01-21 14:51:49.818375
120	113	5	106	2026-01-22 12:13:21.688966
121	114	5	107	2026-01-22 12:25:09.263112
122	115	5	108	2026-01-22 12:52:55.033892
123	116	5	109	2026-01-22 14:11:19.442587
124	117	5	110	2026-01-22 14:23:53.719136
125	118	5	111	2026-01-22 14:25:48.792239
126	119	5	112	2026-01-23 17:28:42.471446
127	120	5	113	2026-01-23 17:30:07.221931
128	121	5	114	2026-01-23 17:43:16.151521
129	122	5	115	2026-01-23 17:44:05.100236
130	123	5	116	2026-01-23 17:45:07.593489
131	124	5	117	2026-01-26 17:34:34.077246
132	125	5	118	2026-01-26 17:35:19.349819
133	126	5	119	2026-01-26 17:40:22.790773
134	127	5	120	2026-01-26 17:43:52.133594
135	128	5	121	2026-01-26 17:44:52.439294
136	129	5	122	2026-01-26 17:46:09.868871
137	130	5	123	2026-01-26 17:47:23.269531
138	131	5	124	2026-01-26 18:15:23.834208
139	132	5	125	2026-01-26 18:15:57.969191
140	133	5	126	2026-01-26 18:17:05.081563
141	134	5	127	2026-01-26 18:26:45.318925
142	135	5	128	2026-01-26 18:27:23.107347
143	136	5	129	2026-01-26 18:27:56.206589
144	137	5	130	2026-01-26 18:28:18.250706
145	138	5	131	2026-01-26 18:28:54.277773
146	139	5	132	2026-01-26 18:29:20.600134
147	140	5	133	2026-01-26 18:29:41.477623
148	141	5	134	2026-01-26 18:30:56.386983
149	142	5	135	2026-01-26 18:31:26.947331
150	143	5	136	2026-01-26 18:34:53.102135
151	144	5	137	2026-01-26 18:35:46.461098
152	145	5	138	2026-01-26 18:36:13.505037
153	146	5	139	2026-02-02 13:22:34.485277
154	147	5	140	2026-02-02 13:37:07.604612
155	148	5	141	2026-02-02 13:37:55.386907
156	149	5	142	2026-02-02 13:39:17.967499
157	150	5	143	2026-02-02 13:39:37.563346
158	151	5	144	2026-02-02 13:39:55.128397
159	152	5	145	2026-02-02 13:40:24.741893
160	153	5	146	2026-02-02 13:41:03.380229
163	156	5	149	2026-02-02 13:46:22.638352
162	155	5	148	2026-02-02 13:45:43.223609
166	159	5	152	2026-02-02 14:48:50.488902
164	157	5	150	2026-02-02 13:47:49.974319
165	158	5	151	2026-02-02 13:48:23.137494
167	160	5	153	2026-02-02 20:06:28.093268
168	161	5	154	2026-02-03 11:20:38.203018
169	162	5	155	2026-02-03 11:29:05.957146
170	163	5	156	2026-02-03 11:30:14.923874
171	164	5	157	2026-02-03 11:30:31.137189
172	165	5	158	2026-02-03 11:30:57.256829
173	166	5	159	2026-02-03 11:31:19.587432
174	167	5	160	2026-02-03 11:31:48.856993
175	168	5	161	2026-02-03 12:53:40.033252
176	169	5	162	2026-02-03 14:04:28.185943
177	170	5	163	2026-02-03 19:51:22.320832
178	171	5	164	2026-02-04 11:54:02.850938
179	172	5	165	2026-02-04 11:54:24.33586
180	173	5	166	2026-02-04 11:54:47.041275
181	174	5	167	2026-02-04 11:55:06.887099
182	175	5	168	2026-02-04 12:00:19.59342
183	176	5	169	2026-02-04 19:56:06.895725
184	177	5	170	2026-02-05 12:14:48.787452
185	178	5	171	2026-02-05 12:17:21.960788
186	179	5	172	2026-02-05 12:17:46.666092
187	180	5	173	2026-02-05 12:18:09.79924
188	181	5	174	2026-02-05 12:18:46.509762
189	182	5	175	2026-02-05 12:19:13.03812
190	183	5	176	2026-02-05 12:19:30.764849
191	184	5	177	2026-02-05 12:21:16.03841
192	185	5	178	2026-02-05 12:21:41.565682
193	186	5	179	2026-02-05 12:21:59.576548
194	187	5	180	2026-02-05 12:22:22.695732
195	188	5	181	2026-02-05 12:22:44.339996
196	189	5	182	2026-02-06 11:24:08.301917
197	190	5	183	2026-02-06 11:34:53.280054
198	191	5	184	2026-02-06 11:35:13.550802
199	192	5	185	2026-02-06 11:35:39.731974
200	193	5	186	2026-02-06 11:36:29.528876
201	194	5	187	2026-02-06 11:38:04.406658
202	195	5	188	2026-02-06 11:38:28.02178
203	196	5	189	2026-02-06 11:39:42.385979
204	197	5	190	2026-02-06 11:41:26.4989
205	198	5	191	2026-02-06 11:42:00.400871
206	199	5	192	2026-02-09 12:33:54.703426
207	200	5	193	2026-02-09 12:49:18.177025
208	201	5	194	2026-02-09 14:11:07.243446
209	202	5	195	2026-02-09 14:11:07.893639
210	203	5	196	2026-02-09 14:11:30.580585
211	204	5	197	2026-02-09 17:23:12.174839
212	205	5	198	2026-02-09 19:08:13.460554
213	206	5	199	2026-02-09 19:08:59.852623
214	207	5	200	2026-02-10 12:17:44.146201
215	208	5	201	2026-02-10 12:18:12.754969
216	209	5	202	2026-02-10 12:21:30.053928
217	210	5	203	2026-02-10 12:21:51.274575
218	211	5	204	2026-02-10 12:22:39.175561
219	212	5	205	2026-02-10 12:22:54.721377
220	213	5	206	2026-02-11 12:06:14.095772
221	214	5	207	2026-02-11 12:07:04.747387
222	215	5	208	2026-02-11 12:08:08.348607
223	216	5	209	2026-02-11 12:08:32.307986
224	217	5	210	2026-02-11 12:08:59.366544
225	218	5	211	2026-02-11 12:09:20.282541
226	219	5	212	2026-02-11 12:09:42.529407
227	220	5	213	2026-02-11 12:10:07.44154
228	221	5	214	2026-02-11 12:10:30.046592
229	222	5	215	2026-02-11 12:10:47.869022
230	223	5	216	2026-02-11 12:11:17.94421
231	224	5	217	2026-02-11 12:11:56.246556
232	225	5	218	2026-02-11 12:57:04.752275
233	226	5	219	2026-02-11 13:58:40.403954
234	227	5	220	2026-02-11 20:34:37.731521
235	228	5	221	2026-02-11 20:35:00.849204
236	229	5	222	2026-02-11 20:35:31.559804
237	230	5	223	2026-02-11 20:36:11.216127
238	231	5	224	2026-02-11 20:37:10.465107
239	232	5	225	2026-02-11 20:37:43.527777
240	233	5	226	2026-02-11 20:38:25.152007
241	234	5	227	2026-02-11 20:39:13.330199
242	235	5	228	2026-02-11 20:39:57.94789
243	236	5	229	2026-02-11 20:40:21.072155
244	237	5	230	2026-02-12 19:01:43.828767
245	238	5	231	2026-02-13 11:42:06.922253
246	239	5	232	2026-02-13 11:42:46.17917
247	240	5	233	2026-02-13 11:43:06.176197
248	241	5	234	2026-02-13 11:43:28.895562
249	242	5	235	2026-02-13 11:44:45.201165
250	243	5	236	2026-02-13 11:45:55.817323
251	244	5	237	2026-02-13 11:47:04.217683
252	245	5	238	2026-02-13 18:09:21.108733
253	246	5	239	2026-02-13 18:09:44.88852
254	247	5	240	2026-02-13 18:12:02.125301
255	248	5	241	2026-02-13 18:15:51.718742
256	249	5	242	2026-02-13 18:16:13.471444
257	250	5	243	2026-02-13 18:16:33.476072
258	251	5	244	2026-02-13 18:16:47.022295
259	252	5	245	2026-02-13 18:17:06.599211
260	253	5	246	2026-02-13 18:18:11.390482
261	254	5	247	2026-02-13 18:18:54.12333
262	255	5	248	2026-02-13 18:19:20.296207
263	256	5	249	2026-02-13 18:19:36.053368
264	257	5	250	2026-02-13 18:20:19.176648
265	258	5	251	2026-02-13 18:20:38.074652
266	259	5	252	2026-02-13 18:21:21.898322
267	260	5	253	2026-02-13 18:21:37.185995
268	261	5	254	2026-02-13 18:21:54.25065
269	262	5	255	2026-02-13 18:23:15.962042
270	263	5	256	2026-02-19 13:34:43.933924
271	264	5	257	2026-02-23 14:22:12.859911
272	265	5	258	2026-02-24 19:36:52.670837
273	266	5	259	2026-02-24 19:37:54.046314
274	267	5	260	2026-02-24 19:38:33.09923
275	268	5	261	2026-02-24 19:38:54.434942
276	269	5	262	2026-02-24 19:39:43.945071
277	270	5	263	2026-02-24 19:40:10.436432
278	271	5	264	2026-02-24 19:40:38.824555
279	272	5	264	2026-02-24 19:40:38.830763
280	273	5	265	2026-02-24 19:43:03.060522
281	274	5	266	2026-02-24 19:43:37.338973
282	275	5	267	2026-02-24 19:44:39.297743
283	276	5	268	2026-02-24 19:45:30.445164
284	277	5	269	2026-02-25 17:44:15.258447
285	278	5	270	2026-02-25 19:07:08.297092
286	279	5	271	2026-02-25 20:01:12.264287
287	280	5	272	2026-02-26 11:27:30.568722
288	281	5	273	2026-02-26 11:27:50.114917
289	282	5	274	2026-02-26 11:28:13.305538
290	283	5	275	2026-02-26 11:28:38.55812
291	284	5	276	2026-02-26 11:29:10.054111
292	285	5	277	2026-02-26 11:29:35.163373
293	286	5	278	2026-02-26 11:30:24.65735
294	287	5	279	2026-02-26 11:30:49.037232
295	288	5	280	2026-02-26 11:31:09.602031
296	289	5	281	2026-02-26 11:31:46.634166
297	290	5	282	2026-02-26 11:32:47.347593
298	291	5	283	2026-02-26 13:01:26.340212
299	292	5	284	2026-02-26 13:15:01.255325
300	293	5	285	2026-02-27 13:20:48.99614
301	294	5	286	2026-02-27 13:21:10.411884
302	295	5	287	2026-02-27 13:21:45.195943
303	296	5	288	2026-02-27 13:22:28.816285
304	297	5	289	2026-02-27 13:22:51.478727
305	298	5	290	2026-02-27 13:23:12.75011
306	299	5	291	2026-02-27 17:09:38.62783
307	300	5	292	2026-02-27 17:11:00.335409
308	301	5	293	2026-02-27 17:11:47.523098
309	302	5	294	2026-02-27 17:13:12.364866
310	303	5	295	2026-02-27 17:16:14.301382
311	304	5	296	2026-02-27 17:17:13.203165
312	305	5	297	2026-02-27 17:17:50.894217
313	306	5	298	2026-02-27 17:18:10.981391
314	307	5	299	2026-02-27 17:41:02.823208
315	308	5	300	2026-03-02 11:07:10.313207
316	309	5	301	2026-03-02 11:18:20.504246
317	310	5	302	2026-03-02 11:18:47.442791
318	311	5	303	2026-03-02 11:19:14.945254
319	312	5	304	2026-03-02 11:19:38.114456
320	313	5	305	2026-03-02 11:19:42.928063
321	314	5	306	2026-03-02 11:20:19.448694
322	315	5	307	2026-03-02 11:21:37.297899
323	316	5	308	2026-03-02 11:22:50.753785
324	317	5	309	2026-03-02 11:34:32.514382
325	318	5	310	2026-03-02 11:35:05.42876
326	319	5	311	2026-03-02 11:35:40.107256
327	320	5	312	2026-03-02 18:07:12.054137
328	321	5	313	2026-03-03 11:10:31.046022
329	322	5	314	2026-03-03 11:10:56.965452
330	323	5	315	2026-03-03 11:11:24.591024
331	324	5	316	2026-03-03 11:11:40.364104
332	325	5	317	2026-03-03 11:12:11.547679
333	326	5	318	2026-03-03 11:12:49.896883
334	327	5	319	2026-03-03 11:13:24.569359
335	328	5	320	2026-03-03 11:54:58.715459
336	329	5	321	2026-03-03 11:56:42.030425
337	330	5	322	2026-03-03 11:58:29.025603
338	331	5	323	2026-03-03 12:08:02.034238
339	332	5	324	2026-03-03 12:56:17.910025
340	333	5	325	2026-03-03 12:57:51.407148
341	334	5	326	2026-03-03 17:35:54.750192
342	335	5	327	2026-03-03 18:46:35.921382
343	336	7	1	2026-03-04 11:31:55.622063
344	337	5	328	2026-03-04 12:05:55.52298
345	338	5	329	2026-03-04 12:06:46.359991
346	339	5	330	2026-03-04 12:07:09.293343
347	340	5	331	2026-03-04 12:07:59.537746
348	341	5	332	2026-03-04 12:08:23.182106
349	342	5	333	2026-03-04 12:10:25.241411
350	343	5	334	2026-03-04 12:11:15.316991
351	344	5	335	2026-03-04 12:11:35.94875
352	345	5	336	2026-03-04 12:11:57.463503
353	346	5	337	2026-03-04 12:12:20.866428
354	347	5	338	2026-03-04 12:12:39.788688
355	348	7	2	2026-03-04 12:14:45.508028
356	349	7	3	2026-03-04 12:18:06.792693
357	350	7	4	2026-03-04 12:23:44.442776
358	351	7	5	2026-03-04 12:24:01.835822
359	352	7	6	2026-03-04 12:24:23.239416
360	353	7	7	2026-03-04 12:24:46.956035
361	354	7	8	2026-03-04 17:04:27.865768
362	355	7	9	2026-03-04 17:05:27.84149
363	356	5	339	2026-03-04 19:41:54.995293
364	357	5	340	2026-03-05 11:30:38.53859
365	358	5	341	2026-03-05 11:51:12.325937
366	359	5	342	2026-03-05 11:59:23.241313
367	360	5	343	2026-03-05 12:00:45.065756
369	362	5	345	2026-03-05 12:01:53.086057
370	363	5	346	2026-03-05 12:05:07.599323
371	364	5	347	2026-03-05 12:05:51.83459
372	365	5	348	2026-03-05 12:06:15.309007
373	366	5	349	2026-03-05 12:11:51.696378
374	367	5	350	2026-03-05 12:12:40.745522
375	368	5	351	2026-03-05 12:13:30.967457
376	369	5	352	2026-03-05 12:13:50.740151
379	372	5	355	2026-03-05 14:36:31.323103
380	373	5	356	2026-03-05 14:37:31.456404
381	374	5	357	2026-03-05 17:27:04.664023
382	375	5	358	2026-03-06 11:51:25.888632
383	376	5	359	2026-03-06 12:11:12.059207
384	377	5	360	2026-03-06 12:11:33.069416
385	378	5	361	2026-03-06 12:13:02.470179
386	379	5	362	2026-03-09 11:35:58.886933
387	380	5	363	2026-03-09 11:37:07.258437
388	381	5	364	2026-03-09 11:40:15.436477
389	382	5	365	2026-03-09 11:41:58.264317
390	383	5	366	2026-03-09 11:42:13.570051
391	384	5	367	2026-03-09 11:42:35.697554
392	385	5	368	2026-03-09 11:43:53.75767
393	386	5	369	2026-03-09 11:44:28.170333
394	387	5	370	2026-03-09 11:44:42.588883
395	388	5	371	2026-03-10 11:16:49.743593
396	389	5	372	2026-03-10 11:17:08.782822
397	390	5	373	2026-03-10 11:18:11.672428
398	391	5	374	2026-03-10 11:18:38.647374
399	392	5	375	2026-03-10 11:19:02.279443
400	393	5	376	2026-03-10 11:19:58.641008
401	394	5	377	2026-03-10 11:20:14.373009
402	395	5	378	2026-03-10 11:20:30.721736
403	396	5	379	2026-03-10 11:21:03.570042
404	397	5	380	2026-03-10 11:21:24.021894
405	398	5	381	2026-03-11 11:33:10.885477
406	399	5	382	2026-03-11 11:34:01.142512
407	400	5	383	2026-03-11 11:35:25.225079
408	401	5	384	2026-03-11 11:35:47.921495
409	402	5	385	2026-03-11 11:36:19.06616
410	403	5	386	2026-03-11 11:37:49.725557
411	404	5	387	2026-03-11 11:41:59.048127
412	405	5	388	2026-03-11 11:49:20.064594
413	406	5	389	2026-03-11 11:49:34.683834
414	407	5	390	2026-03-11 11:51:45.437902
415	408	5	391	2026-03-11 11:52:06.928909
416	409	5	392	2026-03-11 11:57:07.309915
417	410	5	393	2026-03-11 11:57:57.681277
418	411	5	394	2026-03-11 12:32:53.315746
419	412	5	395	2026-03-11 14:24:05.893417
420	413	5	396	2026-03-11 19:08:58.894195
421	419	5	397	2026-03-12 17:53:18.43703
422	420	5	398	2026-03-12 18:06:24.869767
\.


--
-- Data for Name: patient_funnel_status; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.patient_funnel_status (id, patient_id, funnel_status, funnel_temperature, updated_at) FROM stdin;
1	363	Já tem o orçamento mas vai pensar	Quente	2026-03-13 01:10:18.463067
\.


--
-- Data for Name: patient_tag; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.patient_tag (id, patient_id, tag_id, created_at) FROM stdin;
\.


--
-- Data for Name: payment; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.payment (id, appointment_id, patient_id, total_amount, payment_method, installments, status, procedures, consultation_type, created_at, paid_at) FROM stdin;
1	2	2	2850.00	pendente	1	pendente	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1200.0}, {"name": "Preenchimento", "value": 1250.0}]	Particular	2025-11-25 18:52:40.948858	\N
2	13	1	6600.00	pendente	1	pendente	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1200.0}, {"name": "Sculptra", "value": 5000.0}]	Particular	2025-11-27 23:02:34.36257	\N
3	22	17	5600.00	pendente	1	pendente	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1200.0}, {"name": "Ulthera", "value": 4000.0}]	Particular	2025-11-28 19:52:12.559432	\N
4	26	19	1600.00	cartao	1	pago	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1200.0}]	Particular	2025-12-02 13:03:32.021118	2025-12-02 18:52:19.351907
5	28	21	1600.00	pix	1	pago	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1200.0}]	Particular	2025-12-02 14:01:24.822863	2025-12-02 18:52:52.129066
19	79	64	1500.00	pendente	1	pendente	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1100.0}]	Particular	2025-12-11 18:33:23.192568	\N
20	80	65	1600.00	pendente	1	pendente	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1200.0}]	Particular	2025-12-11 19:19:03.137717	\N
31	110	92	1500.00	pendente	1	pendente	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1100.0}]	Particular	2025-12-15 20:03:59.873275	\N
8	45	34	1250.00	cartao_debito	1	pago	[{"name": "Preenchimento", "value": 1250.0}]	Particular	2025-12-04 17:16:19.793621	2025-12-04 18:54:43.573675
32	112	94	6600.00	pendente	1	pendente	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1200.0}, {"name": "Pearl Fracionado", "value": 2500.0}, {"name": "Sculptra", "value": 2500.0}]	Particular	2025-12-16 14:00:58.052355	\N
23	89	74	1100.00	pix	1	pago	[{"name": "Botox", "value": 1100.0}]	Particular	2025-12-12 14:08:04.340142	2025-12-12 14:27:55.67527
21	82	67	1100.00	dinheiro	1	pago	[{"name": "Botox", "value": 1100.0}]	Particular	2025-12-12 12:41:57.738145	2025-12-12 14:29:00.692079
9	61	47	1100.00	cartao	3	pago	[{"name": "Botox", "value": 1100.0}]	Particular	2025-12-09 18:10:25.713989	2025-12-09 19:13:23.81706
11	64	49	1100.00	cartao_debito	1	pago	[{"name": "Botox", "value": 1100.0}]	Particular	2025-12-09 19:09:48.849911	2025-12-09 19:14:56.054454
10	60	46	1000.00	cartao_debito	1	pago	[{"name": "Botox", "value": 1000.0}]	Particular	2025-12-09 18:17:21.158462	2025-12-09 19:15:09.954587
22	85	70	2750.00	cartao	1	pago	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1100.0}, {"name": "Preenchimento", "value": 1250.0}]	Particular	2025-12-12 12:57:43.95068	2025-12-12 15:02:26.638859
12	57	43	1500.00	cartao_debito	1	pago	[{"name": "Preenchimento", "value": 1500.0}]	Particular	2025-12-09 20:34:20.979316	2025-12-09 20:57:23.934891
13	55	41	3700.00	cartao_debito	1	pago	[{"name": "Botox", "value": 1200.0}, {"name": "Preenchimento", "value": 2500.0}]	Particular	2025-12-09 20:53:49.582444	2025-12-09 21:11:08.423951
14	65	50	1.00	dinheiro	1	pago	[{"name": "Botox", "value": 1.0}]	Particular	2025-12-10 17:52:32.854426	2025-12-10 18:00:00.04909
6	32	25	1500.00	pendente	1	pendente	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1100.0}]	Particular	2025-12-02 19:30:47.358773	\N
7	44	33	1600.00	pendente	1	pendente	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1200.0}]	Particular	2025-12-03 18:47:43.850252	\N
33	113	95	1600.00	pendente	1	pendente	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1200.0}]	Particular	2025-12-16 18:32:45.247896	\N
34	115	48	15400.00	pendente	1	pendente	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Sculptra", "value": 5000.0}, {"name": "Preenchimento", "value": 10000.0}]	Particular	2025-12-17 14:07:04.598874	\N
15	69	54	3600.00	cartao	4	pago	[{"name": "Botox", "value": 1100.0}, {"name": "Preenchimento", "value": 2500.0}]	Particular	2025-12-11 12:04:08.034453	2025-12-11 13:40:18.311
16	74	59	1100.00	pendente	1	pendente	[{"name": "Botox", "value": 1100.0}]	Particular	2025-12-11 12:35:39.406943	\N
25	96	78	1100.00	dinheiro	1	pago	[{"name": "Botox", "value": 1100.0}]	Particular	2025-12-12 18:56:58.32232	2025-12-12 19:10:38.703341
17	77	62	2500.00	cartao	3	pago	[{"name": "Botox", "value": 1200.0}, {"name": "Preenchimento", "value": 1300.0}]	Particular	2025-12-11 15:16:39.108464	2025-12-11 17:10:27.986946
18	78	63	1500.00	pendente	1	pendente	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1100.0}]	Particular	2025-12-11 17:59:53.89886	\N
24	92	77	1100.00	dinheiro	1	pago	[{"name": "Botox", "value": 1100.0}]	Particular	2025-12-12 18:56:35.543142	2025-12-12 19:10:45.255243
26	97	81	1200.00	cartao	4	pago	[{"name": "Botox", "value": 1200.0}]	Particular	2025-12-12 19:56:09.474928	2025-12-12 20:01:08.0896
27	98	1	13600.00	pendente	1	pendente	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1200.0}, {"name": "Sculptra", "value": 5000.0}, {"name": "Profhilo", "value": 2000.0}, {"name": "Sculptra", "value": 5000.0}]	Particular	2025-12-12 20:17:35.458983	\N
28	100	83	2500.00	cartao	4	pago	[{"name": "Preenchimento", "value": 2500.0}]	Particular	2025-12-15 13:18:40.231026	2025-12-15 13:25:44.453231
29	99	82	1500.00	pendente	1	pendente	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1100.0}]	Particular	2025-12-15 14:21:11.470988	\N
30	103	86	1500.00	pendente	1	pendente	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1100.0}]	Particular	2025-12-15 18:58:15.396612	\N
36	120	54	4000.00	dinheiro	1	pago	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1100.0}, {"name": "Preenchimento", "value": 2500.0}]	Particular	2026-01-19 17:41:19.136531	2026-01-19 18:36:59.723048
35	119	98	1500.00	dinheiro	1	pago	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1100.0}]	Particular	2026-01-19 17:26:46.688388	2026-01-19 18:37:06.518136
39	118	63	5500.00	cartao	10	pago	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1100.0}, {"name": "Ulthera", "value": 4000.0}]	Particular	2026-01-19 19:40:37.053957	2026-01-19 20:58:11.684455
37	121	99	900.00	cartao_debito	1	pago	[{"name": "Botox", "value": 900.0}]	Particular	2026-01-19 18:54:20.341972	2026-01-19 20:57:58.926931
38	122	100	1600.00	cartao	1	pago	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1200.0}]	Particular	2026-01-19 18:55:09.591013	2026-01-19 20:58:26.563674
41	126	103	1500.00	pendente	1	pendente	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1100.0}]	Particular	2026-01-21 18:04:37.36848	\N
40	128	104	1200.00	cartao_debito	1	pago	[{"name": "Botox", "value": 1200.0}]	Particular	2026-01-21 14:47:13.664122	2026-01-21 14:50:13.497989
42	129	105	1600.00	cartao	3	pago	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1200.0}]	Particular	2026-01-21 18:30:00.600573	2026-01-21 18:45:07.467633
43	130	96	1500.00	pendente	1	pendente	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1100.0}]	Particular	2026-01-21 20:16:32.741589	\N
44	134	109	1600.00	pendente	1	pendente	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1200.0}]	Particular	2026-01-21 20:23:14.043487	\N
45	136	111	1500.00	pendente	1	pendente	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1100.0}]	Particular	2026-01-21 20:24:43.29842	\N
46	142	97	1200.00	pix	1	pago	[{"name": "Botox", "value": 1200.0}]	Particular	2026-01-22 14:22:46.977984	2026-01-22 14:35:12.096243
47	148	122	1200.00	cartao	1	pago	[{"name": "Botox", "value": 1200.0}]	Particular	2026-01-23 19:21:02.7781	2026-01-23 20:30:39.348369
48	147	121	1100.00	cartao_debito	1	pago	[{"name": "Botox", "value": 1100.0}]	Particular	2026-01-23 20:04:23.118086	2026-01-23 20:31:02.670351
49	150	124	3200.00	cartao	3	pago	[{"name": "Botox", "value": 1200.0}, {"name": "Outros", "value": 2000.0}]	Particular	2026-01-26 18:18:55.878332	2026-01-26 18:53:29.310275
50	154	128	2200.00	pendente	1	pendente	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1800.0}]	Particular	2026-01-26 19:51:07.788443	\N
51	157	74	1500.00	pendente	1	pendente	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1100.0}]	Particular	2026-01-27 14:28:35.139151	\N
56	\N	140	1600.00	pendente	1	pendente	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1200.0}]	Particular	2026-01-27 18:35:09.185801	\N
68	250	218	500.00	cartao	1	pago	[{"name": "Pearl Fracionado", "value": 500.0}]	Particular	2026-02-11 17:49:47.055971	2026-02-11 19:14:45.704082
57	\N	147	1400.00	cartao	3	pago	[{"name": "Botox", "value": 1400.0}]	Particular	2026-02-02 14:04:05.290517	2026-02-02 17:51:17.736568
58	\N	159	5500.00	cartao_debito	1	pago	[{"name": "Botox", "value": 1500.0}, {"name": "Ulthera", "value": 4000.0}]	Particular	2026-02-02 15:13:14.651322	2026-02-02 19:52:52.163999
69	252	220	1400.00	cartao	3	pago	[{"name": "Botox", "value": 1400.0}]	Particular	2026-02-11 18:58:21.66372	2026-02-11 19:17:18.074575
60	\N	168	1400.00	cartao	3	pago	[{"name": "Botox", "value": 1400.0}]	Particular	2026-02-03 13:40:43.435406	2026-02-03 14:04:56.615573
67	257	225	1200.00	cartao	4	pago	[{"name": "Botox", "value": 1200.0}]	Particular	2026-02-11 13:57:29.866307	2026-02-11 19:17:59.757418
61	190	162	1000.00	cartao_debito	1	pago	[{"name": "Pearl Fracionado", "value": 1000.0}]	Particular	2026-02-03 17:28:00.079935	2026-02-03 19:54:11.054919
62	199	170	1400.00	cartao	3	pago	[{"name": "Botox", "value": 1400.0}]	Particular	2026-02-03 20:04:17.415748	2026-02-03 21:05:00.98436
63	202	173	14000.00	cartao	2	pago	[{"name": "Botox", "value": 14000.0}]	Particular	2026-02-04 17:32:21.65239	2026-02-04 19:56:58.566014
70	265	232	1200.00	cartao	1	pago	[{"name": "Botox", "value": 1200.0}]	Particular	2026-02-12 18:37:21.580249	2026-02-12 19:16:30.500962
65	\N	182	1200.00	cartao	3	pago	[{"name": "Botox", "value": 1200.0}]	Particular	2026-02-05 18:01:03.415157	2026-02-05 18:05:50.895769
66	217	188	3700.00	cartao	3	pago	[{"name": "Botox", "value": 1200.0}, {"name": "Sculptra", "value": 2500.0}]	Particular	2026-02-05 19:34:58.218208	2026-02-05 21:12:05.09693
64	\N	180	1200.00	cartao_debito	1	pago	[{"name": "Botox", "value": 1200.0}]	Particular	2026-02-05 14:36:32.642183	2026-02-05 21:12:19.20153
71	272	239	1400.00	cartao_debito	1	pago	[{"name": "Preenchimento", "value": 1400.0}]	Particular	2026-02-13 13:29:30.729849	2026-02-13 16:43:51.784888
72	300	262	1400.00	cartao	2	pago	[{"name": "Botox", "value": 1400.0}]	Particular	2026-02-13 18:40:32.291792	2026-02-13 20:26:15.173573
73	285	248	1600.00	pendente	1	pendente	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1200.0}]	Particular	2026-02-19 20:30:43.414147	\N
74	292	254	1800.00	pendente	1	pendente	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1400.0}]	Particular	2026-02-20 18:55:42.959781	\N
75	295	257	1800.00	pendente	1	pendente	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1400.0}]	Particular	2026-02-20 18:57:25.950216	\N
76	302	103	2900.00	pendente	1	pendente	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1100.0}, {"name": "Preenchimento", "value": 1400.0}]	Particular	2026-02-20 18:59:27.402297	\N
77	299	261	1600.00	pendente	1	pendente	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1200.0}]	Particular	2026-02-20 19:28:15.842683	\N
78	305	265	1800.00	pix	1	pago	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1400.0}]	Particular	2026-02-25 12:57:29.162412	2026-02-25 13:00:25.673259
79	349	305	3400.00	pendente	1	pendente	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1200.0}, {"name": "Preenchimento", "value": 1800.0}]	Particular	2026-02-27 19:36:04.384566	\N
80	350	306	1800.00	pendente	1	pendente	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1400.0}]	Particular	2026-02-27 19:57:05.921521	\N
81	346	302	1800.00	pendente	1	pendente	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1400.0}]	Particular	2026-02-27 19:57:37.102205	\N
88	380	333	1200.00	cartao	1	pago	[{"name": "Botox", "value": 1200.0}]	Particular	2026-03-03 20:31:55.795401	2026-03-03 20:38:38.896413
83	359	315	2700.00	cartao	3	pago	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1100.0}, {"name": "Preenchimento", "value": 1200.0}]	Particular	2026-03-02 17:51:11.202503	2026-03-02 20:46:08.116422
85	366	320	1600.00	cartao	3	pago	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1200.0}]	Particular	2026-03-02 19:21:15.568491	2026-03-02 20:46:44.258412
84	360	316	4700.00	cartao	2	pago	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1800.0}, {"name": "Sculptra", "value": 2500.0}]	Particular	2026-03-02 19:19:49.774228	2026-03-02 20:46:26.388021
86	362	317	1600.00	cartao_debito	1	pago	[{"name": "Consulta Particular", "value": 400.0}, {"name": "Botox", "value": 1200.0}]	Particular	2026-03-02 19:27:59.316334	2026-03-02 20:46:33.556852
82	353	309	1400.00	cartao	2	pago	[{"name": "Botox", "value": 1400.0}]	Particular	2026-03-02 13:17:43.356373	2026-03-02 20:47:00.112227
87	364	319	1200.00	cartao	2	pago	[{"name": "Botox", "value": 1200.0}]	Particular	2026-03-02 20:40:21.111992	2026-03-02 20:47:10.928921
90	397	342	1200.00	cartao	3	pago	[{"name": "Botox", "value": 1200.0}]	Particular	2026-03-04 18:00:50.553436	2026-03-04 18:10:02.713258
89	396	341	1200.00	cartao	1	pago	[{"name": "Botox", "value": 1200.0}]	Particular	2026-03-04 15:00:02.27904	2026-03-04 17:32:21.169513
91	411	356	1200.00	cartao	1	pago	[{"name": "Botox", "value": 1200.0}]	Particular	2026-03-04 19:58:32.723074	2026-03-05 01:23:04.356655
92	427	369	1400.00	cartao_debito	1	pago	[{"name": "Botox", "value": 1400.0}]	Particular	2026-03-05 20:49:11.441626	2026-03-05 20:50:43.809748
93	441	259	6000.00	cartao	1	pago	[{"name": "Sculptra", "value": 6000.0}]	particular	2026-03-09 13:14:16.244762	2026-03-09 13:47:04.250169
94	455	390	1100.00	cartao	3	pago	[{"name": "Botox", "value": 1100.0}]	Particular	2026-03-10 13:07:18.490925	2026-03-10 13:10:03.988808
95	458	393	1100.00	cartao	1	pago	[{"name": "Botox", "value": 1100.0}]	particular	2026-03-10 18:41:00.001058	2026-03-10 19:17:44.590521
96	459	394	1100.00	cartao_debito	1	pago	[{"name": "Botox", "value": 1100.0}]	particular	2026-03-10 18:52:43.290785	2026-03-10 19:18:28.009775
98	485	412	1400.00	cartao_debito	1	pago	[{"name": "Botox", "value": 1400.0}]	particular	2026-03-11 15:26:06.353399	2026-03-11 17:59:21.052036
97	463	219	9500.00	cartao	10	pago	[{"name": "Pearl Fracionado", "value": 2500.0}, {"name": "Sculptra", "value": 5000.0}, {"name": "Ulthera", "value": 2000.0}]	particular	2026-03-11 13:01:39.432436	2026-03-11 18:09:50.429564
99	\N	382	20000.00	cartao	10	pago	[{"name": "Morpheus", "value": 20000.0}]	particular	2026-03-12 12:22:11.558835	2026-03-12 18:09:08.480675
101	477	363	5000.00	cartao	10	pago	[{"name": "Sculptra", "value": 5000.0}]	particular	2026-03-12 17:59:08.871142	2026-03-12 18:09:46.752904
100	476	61	4300.00	cartao	6	pago	[{"name": "Botox", "value": 1100.0}, {"name": "Preenchimento", "value": 2800.0}, {"name": "Outros", "value": 400.0}]	particular	2026-03-12 17:57:30.010448	2026-03-12 18:12:22.34429
103	480	224	1000.00	pendente	1	pendente	[{"name": "LIMELIGHT FACE", "value": 1000.0}]	particular	2026-03-12 19:19:11.225763	\N
102	492	420	2500.00	cartao	1	pago	[{"name": "Outros", "value": 2500.0}]	particular	2026-03-12 18:36:27.872472	2026-03-13 01:40:42.304419
\.


--
-- Data for Name: plan_cp; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.plan_cp (id, encounter_id, indication_status, case_type, selected_procedures, lipo_areas, implant_plane, implant_profile, implant_volume_min, implant_volume_max, technologies, internacao, estimated_time, follow_up_deadline, reception_obs) FROM stdin;
1	1	\N	\N	[]	[]			\N	\N	[]			7d	
2	2	YES	PRIMARY	["Ritidoplastia (Face)"]	[]			\N	\N	["Renuvion"]				
\.


--
-- Data for Name: prescription; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.prescription (id, patient_id, doctor_id, appointment_id, medications_oral, medications_topical, summary, prescription_type, created_at) FROM stdin;
1	1	5	\N	[]	[{"instructions": "Aplicar 1mL na \\u00e1rea afetada do couro cabeludo 2 vezes ao dia", "medication": "Minoxidil 5% solu\\u00e7\\u00e3o capilar", "type": "topical"}]	\N	dermascribe	2025-12-12 20:26:50.300168
2	95	5	\N	[]	[{"brand": null, "id": 88, "instructions": "aplicar no rosto \\u00c0 noite e retirar pela manh\\u00e3", "medication": "ADACNE", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-02-06 18:00:57.942856
3	222	5	\N	[]	[]	\N	dermascribe	2026-02-11 19:30:06.955379
4	222	5	\N	[]	[{"brand": null, "id": 124, "instructions": "aplicar no rosto \\u00c0 noite e retirar pela manh\\u00e3", "medication": "Esthederm Intensive Pro-Collagen+ - Creme", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-02-11 19:31:03.569784
5	222	5	\N	[]	[{"brand": null, "id": 124, "instructions": "aplicar no rosto \\u00c0 noite e retirar pela manh\\u00e3", "medication": "Esthederm Intensive Pro-Collagen+ - Creme", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-02-12 20:04:50.543202
6	222	5	\N	[]	[{"brand": null, "id": 125, "instructions": "aplicar nas areas dos olhos 2x/dia", "medication": "Esthederm Intensive Retinol Eye Lifting", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-02-12 20:09:18.149149
7	222	5	\N	[{"medication": "NEOSIL ATTACK", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA POR 3 MESES"}, {"medication": "MINOXIDIL 2,5MG", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA"}]	[{"medication": "CAPPY", "type": "topical", "instructions": "APLICAR NO COURO CABELUDO 1X/DIA"}]	\N	dermascribe	2026-02-12 20:38:30.904347
8	222	5	\N	[{"medication": "NEOSIL ATTACK", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA POR 3 MESES"}, {"medication": "MINOXIDIL 2,5MG", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA"}]	[{"medication": "CAPPY", "type": "topical", "instructions": "APLICAR NO COURO CABELUDO 1X/DIA"}]	\N	dermascribe	2026-02-12 20:43:57.7225
9	222	5	\N	[{"medication": "NEOSIL ATTACK", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA POR 3 MESES"}, {"medication": "MINOXIDIL 2,5MG", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA"}]	[{"medication": "CAPPY", "type": "topical", "instructions": "APLICAR NO COURO CABELUDO 1X/DIA"}]	\N	dermascribe	2026-02-12 20:45:58.784213
10	222	5	\N	[{"medication": "NEOSIL ATTACK", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA POR 3 MESES"}, {"medication": "MINOXIDIL 2,5MG", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA"}]	[{"medication": "CAPPY", "type": "topical", "instructions": "APLICAR NO COURO CABELUDO 1X/DIA"}]	\N	dermascribe	2026-02-12 20:48:28.425071
11	242	5	\N	[{"medication": "NEOSIL ATTACK", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA POR 3 MESES"}, {"medication": "MINOXIDIL 2,5MG", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA"}]	[{"medication": "CAPPY", "type": "topical", "instructions": "APLICAR NO COURO CABELUDO 1X/DIA"}]	\N	dermascribe	2026-02-13 14:27:19.890544
12	247	5	\N	[{"brand": null, "id": 263, "instructions": "TOMAR 1 CP VO POR DIA 2 HORAS ANTES DE DORMIR POR 15 DIAS", "medication": "hixizine 25mg", "purpose": null, "type": "oral"}]	[{"brand": null, "id": 294, "instructions": "aplicar no corpo 2X/DIA E SE COCEIRA", "medication": "neutrogena formula norueguesa", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-02-19 13:28:06.697299
13	135	5	\N	[{"brand": null, "id": 303, "instructions": "tomar 3 cp vo por dia por 3 dias, depois 2 cp vo por mais 4 dias, depois 1 cp vo por mais 3 dias", "medication": "predsin 20mg", "purpose": null, "type": "oral"}]	[]	\N	dermascribe	2026-02-19 13:59:35.650975
14	248	5	\N	[{"brand": null, "id": 291, "instructions": "Tomar 1cp vo uma vez ao dia", "medication": "minoxidil 0,5 mg", "purpose": null, "type": "oral"}]	[]	\N	dermascribe	2026-02-19 14:42:53.390306
15	249	5	\N	[{"medication": "NEOSIL ATTACK", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA POR 3 MESES"}, {"medication": "MINOXIDIL 2,5MG", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA"}]	[{"medication": "CAPPY", "type": "topical", "instructions": "APLICAR NO COURO CABELUDO 1X/DIA"}]	\N	dermascribe	2026-02-19 19:49:45.912824
16	252	5	\N	[{"medication": "MINOXIDIL 2,5MG", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA"}, {"brand": null, "id": 183, "instructions": "TOMAR 1 CP VO POR DIA POR 3 MESES", "medication": "anacaps activ", "purpose": null, "type": "oral"}, {"brand": null, "id": 242, "instructions": "tomar 1 cp vo por dia (uso continuo)", "medication": "dutasterida 0,5mg", "purpose": null, "type": "oral"}]	[{"medication": "CAPPY", "type": "topical", "instructions": "APLICAR NO COURO CABELUDO 1X/DIA"}]	\N	dermascribe	2026-02-19 20:10:23.456148
17	256	5	\N	[{"medication": "MINOXIDIL 2,5MG", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA"}]	[]	\N	dermascribe	2026-02-20 14:26:25.19556
18	265	5	\N	[]	[{"medication": "RETINOL BOOST NEUTROGENA", "type": "topical", "instructions": "aplicar no rosto \\u00c0 noite e retirar pela manh\\u00e3"}, {"brand": null, "id": 169, "instructions": "APLICAR NOR OSTO \\u00e0 NOITE E RETIRAR PELA MANH\\u00c3", "medication": "VITACIDPLUS", "purpose": null, "type": "topical"}, {"brand": "ACTINE", "id": 177, "instructions": "aplicar pela masnh\\u00e3 antes do protetor", "medication": "actine vitamina c", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-02-25 12:52:50.263005
19	266	5	\N	[]	[{"brand": null, "id": 231, "instructions": "APLICAR NO ROSTO \\u00e0 NOITE E RETIRAR PELA MANH\\u00c3 ( INTERCALADO COM DERMOPURE DA EUCERIN)", "medication": "diferin 0,3", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-02-25 13:22:30.564793
20	268	5	\N	[{"brand": "Mantecorp", "id": 213, "instructions": "tomar 1 sachet por dia por 3 meses", "medication": "collagen h.a mantecorp", "purpose": null, "type": "oral"}]	[{"brand": null, "id": 131, "instructions": "APLICAR NO ROSTO \\u00e0 NOITE E RETIRAR PELA MANH\\u00c3", "medication": "Hyaluron-Filler S\\u00e9rum Epigenetic", "purpose": null, "type": "topical"}, {"brand": null, "id": 252, "instructions": "APLICAR NO ROSTO PELA MANHA ANTES DO FPS", "medication": "essencele c 20", "purpose": "ACHE", "type": "topical"}]	\N	dermascribe	2026-02-25 14:02:56.703192
21	267	5	\N	[]	[{"brand": null, "id": 332, "instructions": "aplicar no rosto \\u00c0 noite e retirar pela manh\\u00e3", "medication": "RETINOL BOOST NEUTROGENA", "purpose": null, "type": "topical"}, {"brand": null, "id": 120, "instructions": "LAVAR O ROSTO 2X/DIA", "medication": "EFACLAR GEL CONCETRADO", "purpose": null, "type": "topical"}, {"brand": null, "id": 122, "instructions": "APLICAR NO ROSTO 3-4X/DIA", "medication": "EPIDRAT CALM", "purpose": null, "type": "topical"}, {"brand": null, "id": 86, "instructions": "aplicar no rosto 2x/dia", "medication": "isdin fusion water", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-02-25 14:23:24.745931
22	273	5	\N	[{"medication": "NEOSIL ATTACK", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA POR 3 MESES"}, {"medication": "MINOXIDIL 2,5MG", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA"}]	[{"medication": "CAPPY", "type": "topical", "instructions": "APLICAR NO COURO CABELUDO 1X/DIA"}]	\N	dermascribe	2026-02-25 17:48:03.795066
23	273	5	\N	[]	[{"brand": null, "id": 326, "instructions": "aplicar em cima das verrugas 1x/dia POR 3-5 DIAS, REUTILIZAR SE NECESSARIO", "medication": "verrux", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-02-25 18:14:43.660694
24	292	5	\N	[{"medication": "NEOSIL ATTACK", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA POR 3 MESES"}, {"medication": "MINOXIDIL 2,5MG", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA"}, {"brand": null, "id": 126, "instructions": "TOMAR 1 CP VO POR DIA", "medication": "FINASTERIDA 1MG", "purpose": null, "type": "oral"}]	[{"medication": "CAPPY", "type": "topical", "instructions": "APLICAR NO COURO CABELUDO 1X/DIA"}, {"medication": "vitacid 0,025", "type": "topical", "instructions": "aplicar no couro cabeludo 1x/dia \\u00e0 noite e lavar pela manh\\u00e3"}]	\N	dermascribe	2026-02-26 13:16:21.158741
25	282	5	\N	[]	[{"brand": null, "id": 332, "instructions": "aplicar no rosto \\u00c0 noite e retirar pela manh\\u00e3", "medication": "RETINOL BOOST NEUTROGENA", "purpose": null, "type": "topical"}, {"brand": "Eucerin", "id": 1, "instructions": "Clareamento de manchas e uniformiza\\u00e7\\u00e3o do tom da pele", "medication": "Anti-Pigment Dual S\\u00e9rum", "purpose": null, "type": "topical"}, {"brand": "ACTINE", "id": 177, "instructions": "aplicar pela masnh\\u00e3 antes do protetor", "medication": "actine vitamina c", "purpose": null, "type": "topical"}, {"brand": null, "id": 227, "instructions": "lavar o rosto 2x/dia", "medication": "dermotivin original", "purpose": null, "type": "topical"}, {"brand": null, "id": 150, "instructions": "LAVAR O COURO CABELUDO 2-3X POR SEMANA", "medication": "PIELLUS SHAMPOO", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-02-26 14:00:26.152651
26	291	5	\N	[]	[{"brand": null, "id": 103, "instructions": "APLICAR NAS MAOS 1X/DIA \\u00c0 NOITE E OCLUIR COM LUVA", "medication": "CLOBETASOL POMADA", "purpose": null, "type": "topical"}, {"brand": null, "id": 198, "instructions": "aplicar em baixo dos seios", "medication": "bepantol baby", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-02-26 14:11:39.102667
27	288	5	\N	[]	[{"brand": null, "id": 169, "instructions": "APLICAR NO ROSTO \\u00e0 NOITE E RETIRAR PELA MANH\\u00c3", "medication": "VITACIDPLUS", "purpose": null, "type": "topical"}, {"brand": "Eucerin", "id": 1, "instructions": "Clareamento de manchas e uniformiza\\u00e7\\u00e3o do tom da pele", "medication": "Anti-Pigment Dual S\\u00e9rum", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-02-27 13:20:45.385496
28	295	5	\N	[{"brand": null, "id": 146, "instructions": "TOMAR 1 CP VO POR DIA POR 3 MESES", "medication": "NEOSIL ATTACK", "purpose": null, "type": "oral"}]	[{"brand": null, "id": 134, "instructions": "APLICAR  NOS FIOS 1X/SEMANA AP\\u00d3S LAVAGEM COM SHAMPOO", "medication": "KERASOLUTION MASCARA CAPILAR", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-02-27 13:56:20.36762
29	296	5	\N	[{"medication": "MINOXIDIL 2,5MG", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA"}, {"brand": null, "id": 126, "instructions": "TOMAR 1 CP VO POR DIA", "medication": "FINASTERIDA 1MG", "purpose": null, "type": "oral"}]	[{"brand": null, "id": 148, "instructions": "APLICAR NO COURO CABELUDO 1X/DIA \\u00e0 NOITE", "medication": "PANT SEC", "purpose": null, "type": "topical"}, {"brand": null, "id": 111, "instructions": "aplicar nos fios do cabelo ap\\u00f3s lavagem com shampo. 1x/semana", "medication": "DERCOS KERASOLUTION HIDRATANTE CAPILAR", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-02-27 14:14:53.725849
30	297	5	\N	[]	[{"brand": "Eucerin", "id": 8, "instructions": "Preenchimento de rugas durante a noite", "medication": "Hyaluron-Filler Creme Facial Noite", "purpose": null, "type": "topical"}, {"brand": "Mantecorp", "id": 47, "instructions": "S\\u00e9rum com retinol para renova\\u00e7\\u00e3o celular e redu\\u00e7\\u00e3o de linhas finas", "medication": "Reviline Retinol S\\u00e9rum", "purpose": null, "type": "topical"}, {"brand": null, "id": 131, "instructions": "APLICAR NO ROSTO \\u00e0 NOITE E RETIRAR PELA MANH\\u00c3", "medication": "Hyaluron-Filler S\\u00e9rum Epigenetic", "purpose": null, "type": "topical"}, {"brand": null, "id": 192, "instructions": "APLICAR NO CORPO 3-4X/DIA", "medication": "atoderm gel creme", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-02-27 15:00:18.994066
31	297	5	\N	[]	[{"brand": "Eucerin", "id": 8, "instructions": "aplicar no rosto \\u00e0 noite e retirar pela manh\\u00e3", "medication": "Hyaluron-Filler Creme Facial Noite", "purpose": null, "type": "topical"}, {"brand": "Mantecorp", "id": 47, "instructions": "aplicar no rosto \\u00e0 noite e retirar pela manh\\u00e3", "medication": "Reviline Retinol S\\u00e9rum", "purpose": null, "type": "topical"}, {"brand": null, "id": 131, "instructions": "aplicar pela manh\\u00e3 antes do protetor", "medication": "Hyaluron-Filler S\\u00e9rum Epigenetic", "purpose": null, "type": "topical"}, {"brand": null, "id": 192, "instructions": "APLICAR NO CORPO 3-4X/DIA", "medication": "atoderm gel creme", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-02-27 15:03:48.02978
32	303	5	\N	[{"medication": "NEOSIL ATTACK", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA POR 3 MESES"}, {"medication": "MINOXIDIL 2,5MG", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA"}]	[{"medication": "CAPPY", "type": "topical", "instructions": "APLICAR NO COURO CABELUDO 1X/DIA"}]	\N	dermascribe	2026-02-27 19:41:28.067306
33	311	5	\N	[]	[{"brand": null, "id": 161, "instructions": "APLICAR NO ROSTO 2X/DIA", "medication": "SUNFRESH OIL CONTROL FPS80 NEUTROGENA", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-03-02 13:31:43.526174
34	318	5	\N	[{"brand": null, "id": 126, "instructions": "TOMAR 1 CP VO POR DIA", "medication": "FINASTERIDA 1MG", "purpose": null, "type": "oral"}]	[]	\N	dermascribe	2026-03-02 20:08:02.799745
35	321	5	\N	[{"brand": null, "id": 146, "instructions": "TOMAR 1 CP VO POR DIA POR 3 MESES", "medication": "NEOSIL ATTACK", "purpose": null, "type": "oral"}, {"brand": null, "id": 291, "instructions": "Tomar 1cp vo uma vez ao dia", "medication": "minoxidil 0,5 mg", "purpose": null, "type": "oral"}]	[{"medication": "Shampoo Anticaspa Pielus DI", "type": "topical", "instructions": "lavar o couro cabeludo 3x/semana"}, {"brand": null, "id": 333, "instructions": "aplicar no rosto \\u00e0 noite e retirar pela manh\\u00e3", "medication": "vitacid 0,025", "purpose": null, "type": "topical"}, {"brand": null, "id": 332, "instructions": "aplicar no rosto \\u00c0 noite e retirar pela manh\\u00e3", "medication": "RETINOL BOOST NEUTROGENA", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-03-03 12:37:21.726864
36	322	5	\N	[{"brand": null, "id": 291, "instructions": "Tomar 1cp vo uma vez ao dia", "medication": "minoxidil 0,5 mg", "purpose": null, "type": "oral"}]	[]	\N	dermascribe	2026-03-03 13:06:52.835305
37	324	5	\N	[]	[{"brand": null, "id": 329, "instructions": "aplicar no rosto \\u00c0 noite e retirar pela manh\\u00e3", "medication": "zella", "purpose": null, "type": "topical"}, {"brand": "Eucerin", "id": 1, "instructions": "Clareamento de manchas e uniformiza\\u00e7\\u00e3o do tom da pele", "medication": "Anti-Pigment Dual S\\u00e9rum", "purpose": null, "type": "topical"}, {"brand": null, "id": 243, "instructions": "lavar o rosto 2x/dia", "medication": "efaclar alta tolerancia", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-03-03 13:46:08.327388
56	377	5	\N	[{"medication": "NEOSIL ATTACK", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA POR 3 MESES"}, {"medication": "MINOXIDIL 2,5MG", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA"}, {"brand": null, "id": 263, "instructions": "TOMAR 1 CP VO POR DIA 2 HORAS ANTES DE DORMIR", "medication": "hixizine 25mg", "purpose": null, "type": "oral"}]	[{"medication": "CAPPY", "type": "topical", "instructions": "APLICAR NO COURO CABELUDO 1X/DIA"}]	\N	dermascribe	2026-03-06 13:21:06.951077
38	325	5	\N	[{"brand": null, "id": 144, "instructions": "TOMAR 1 CP VO POR DIA (USO CONTINUO)", "medication": "MINOXIDIL 2,5 MG", "purpose": null, "type": "oral"}]	[{"brand": null, "id": 168, "instructions": "aplicar nos bra\\u00e7os 1x/dia \\u00c0 noite", "medication": "UREIA -------------- 20% ACIDO SALICILICO -------------- 4% LACTATO DE AMONIO -------------- 12% CREME HIDRATANTE -------------- 250 G", "purpose": null, "type": "topical"}, {"brand": "Mantecorp", "id": 48, "instructions": "aplicar nos bra\\u00e7os 2x/semana \\u00c0 noite e lavar pela manh\\u00e3", "medication": "Glycare S\\u00e9rum", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-03-03 14:14:18.578537
39	326	5	\N	[]	[{"brand": null, "id": 195, "instructions": "aplicar no rosto \\u00c0 noite e retirar pela manh\\u00e3", "medication": "azelan gel", "purpose": null, "type": "topical"}, {"brand": "AVENE", "id": 207, "instructions": "LAVAR O ROSTO 2X/DIA", "medication": "cleanance gel", "purpose": null, "type": "topical"}, {"brand": null, "id": 86, "instructions": "aplicar no rosto 2x/dia", "medication": "isdin fusion water", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-03-03 14:36:33.857605
40	326	5	\N	[{"brand": null, "id": 143, "instructions": "TOMAR 1 CP VO POR DIA", "medication": "MINOXIDIL 1MG (USO CONTINUO)", "purpose": null, "type": "oral"}]	[{"brand": null, "id": 85, "instructions": "Aplicar 1mL na \\u00e1rea afetada do couro cabeludo 2 vezes ao dia", "medication": "Minoxidil 5% solu\\u00e7\\u00e3o capilar", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-03-03 15:14:15.580143
41	331	5	\N	[{"brand": null, "id": 143, "instructions": "TOMAR 1 CP VO POR DIA", "medication": "MINOXIDIL 1MG (USO CONTINUO)", "purpose": null, "type": "oral"}]	[{"brand": null, "id": 85, "instructions": "Aplicar 1mL na \\u00e1rea afetada do couro cabeludo 2 vezes ao dia", "medication": "Minoxidil 5% solu\\u00e7\\u00e3o capilar", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-03-03 15:33:36.184541
42	334	5	\N	[{"brand": null, "id": 242, "instructions": "tomar 1 cp vo 3 x/semana", "medication": "dutasterida 0,5mg", "purpose": null, "type": "oral"}, {"brand": null, "id": 144, "instructions": "TOMAR 1 CP VO POR DIA (USO CONTINUO)", "medication": "MINOXIDIL 2,5 MG", "purpose": null, "type": "oral"}]	[]	\N	dermascribe	2026-03-03 18:23:01.754929
43	330	5	\N	[{"brand": null, "id": 146, "instructions": "TOMAR 1 CP VO POR DIA POR 3 MESES", "medication": "NEOSIL ATTACK", "purpose": null, "type": "oral"}]	[{"brand": null, "id": 224, "instructions": "APLICAR NO ROSTO \\u00e0 NOITE E RETIRAR PELA MANH\\u00c3", "medication": "derivamicro", "purpose": null, "type": "topical"}, {"brand": "AVENE", "id": 207, "instructions": "LAVAR O ROSTO 2X/DIA", "medication": "cleanance gel", "purpose": null, "type": "topical"}, {"brand": null, "id": 86, "instructions": "aplicar no rosto 2x/dia", "medication": "isdin fusion water", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-03-03 18:51:18.920297
44	333	5	\N	[]	[{"brand": "Eucerin", "id": 5, "instructions": "Clareamento de manchas em \\u00e1reas espec\\u00edficas do corpo", "medication": "Anti-Pigment Creme Corporal para \\u00c1reas Espec\\u00edficas", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-03-03 20:33:13.497482
45	337	5	\N	[{"brand": null, "id": 126, "instructions": "TOMAR 1 CP VO POR DIA", "medication": "FINASTERIDA 1MG", "purpose": null, "type": "oral"}, {"brand": null, "id": 291, "instructions": "Tomar 1cp vo uma vez ao dia", "medication": "minoxidil 0,5 mg", "purpose": null, "type": "oral"}]	[]	\N	dermascribe	2026-03-04 12:45:52.357846
46	229	5	\N	[{"brand": null, "id": 291, "instructions": "Tomar 1cp vo uma vez ao dia", "medication": "minoxidil 0,5 mg", "purpose": null, "type": "oral"}, {"brand": null, "id": 146, "instructions": "TOMAR 1 CP VO POR DIA POR 3 MESES", "medication": "NEOSIL ATTACK", "purpose": null, "type": "oral"}]	[{"brand": null, "id": 279, "instructions": "APLICAR NOS FIOS DO CABELO 1X/SEMANA AP\\u00d3S LAVAGEM COM SHAMPOO", "medication": "kerasoluiton mascara capilar", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-03-04 13:12:08.571419
47	338	5	\N	[]	[{"brand": null, "id": 252, "instructions": "APLICAR NO ROSTO PELA MANHA ANTES DO FPS", "medication": "essencele c 20", "purpose": "ACHE", "type": "topical"}]	\N	dermascribe	2026-03-04 13:38:16.627382
48	341	5	\N	[]	[{"brand": null, "id": 332, "instructions": "aplicar no rosto \\u00c0 noite e retirar pela manh\\u00e3", "medication": "RETINOL BOOST NEUTROGENA", "purpose": null, "type": "topical"}, {"brand": "Eucerin", "id": 1, "instructions": "APLICAR NO ROSTO \\u00c0 NOITE E RETIRAR PELA MANH\\u00c3", "medication": "Anti-Pigment Dual S\\u00e9rum", "purpose": null, "type": "topical"}, {"brand": "Eucerin", "id": 5, "instructions": "APLICAR NA VIRILHA 1-2X/DIA", "medication": "Anti-Pigment Creme Corporal para \\u00c1reas Espec\\u00edficas", "purpose": null, "type": "topical"}, {"brand": null, "id": 252, "instructions": "APLICAR NO ROSTO PELA MANHA ANTES DO FPS", "medication": "essencele c 20", "purpose": "ACHE", "type": "topical"}]	\N	dermascribe	2026-03-04 14:51:46.47667
49	342	5	\N	[]	[{"brand": null, "id": 332, "instructions": "aplicar no rosto \\u00c0 noite e retirar pela manh\\u00e3", "medication": "RETINOL BOOST NEUTROGENA", "purpose": null, "type": "topical"}, {"medication": "Creme Anti-Idade Profuse Densifiant Fondant", "type": "topical", "instructions": "aplicar no rosto \\u00c0 noite e retirar pela manh\\u00e3"}, {"medication": "Creme Noturno Healthy Renew", "type": "topical", "instructions": "APLICAR NO ROSTO PELA MANH\\u00c3 ANTES DO PROTETOR"}]	\N	dermascribe	2026-03-04 18:00:06.131202
50	343	5	\N	[{"medication": "NEOSIL ATTACK", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA POR 3 MESES"}, {"medication": "MINOXIDIL 2,5MG", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA"}]	[{"medication": "CAPPY", "type": "topical", "instructions": "APLICAR NO COURO CABELUDO 1X/DIA"}]	\N	dermascribe	2026-03-04 18:24:00.312132
51	360	5	\N	[]	[]	\N	dermascribe	2026-03-05 14:11:18.768345
52	360	5	\N	[{"medication": "NEOSIL ATTACK", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA POR 3 MESES"}, {"medication": "MINOXIDIL 2,5MG", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA"}]	[{"medication": "CAPPY", "type": "topical", "instructions": "APLICAR NO COURO CABELUDO 1X/DIA"}]	\N	dermascribe	2026-03-05 14:11:34.915722
53	374	5	\N	[{"brand": null, "id": 291, "instructions": "Tomar 1cp vo uma vez ao dia", "medication": "minoxidil 0,5 mg", "purpose": null, "type": "oral"}]	[]	\N	dermascribe	2026-03-05 19:06:23.108748
54	366	5	\N	[{"medication": "MINOXIDIL 2,5MG", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA"}]	[{"medication": "CAPPY", "type": "topical", "instructions": "APLICAR NO COURO CABELUDO 1X/DIA"}]	\N	dermascribe	2026-03-05 19:33:54.953272
55	368	5	\N	[{"medication": "NEOSIL ATTACK", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA POR 3 MESES"}, {"medication": "MINOXIDIL 2,5MG", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA"}, {"brand": null, "id": 126, "instructions": "TOMAR 1 CP VO POR DIA", "medication": "FINASTERIDA 1MG", "purpose": null, "type": "oral"}]	[{"medication": "CAPPY", "type": "topical", "instructions": "APLICAR NO COURO CABELUDO 1X/DIA"}]	\N	dermascribe	2026-03-05 19:45:51.48983
57	378	5	\N	[]	[{"brand": null, "id": 332, "instructions": "aplicar no rosto \\u00c0 noite e retirar pela manh\\u00e3", "medication": "RETINOL BOOST NEUTROGENA", "purpose": null, "type": "topical"}, {"brand": null, "id": 252, "instructions": "APLICAR NO ROSTO PELA MANHA ANTES DO FPS", "medication": "essencele c 20", "purpose": "ACHE", "type": "topical"}, {"brand": "Eucerin", "id": 20, "instructions": "Limpeza profunda para pele oleosa e acneica", "medication": "DermoPure Oil Control Gel de Limpeza", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-03-06 14:21:34.608163
58	379	5	\N	[{"medication": "MINOXIDIL 2,5MG", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA"}]	[]	\N	dermascribe	2026-03-09 13:25:18.976841
59	380	5	\N	[]	[{"brand": null, "id": 179, "instructions": "aplicar nas lesoes 1x/dia por 30 dias", "medication": "advatan", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-03-09 13:41:07.597661
60	238	5	\N	[]	[{"brand": null, "id": 264, "instructions": "aplicar 2x/dia NAS LESOES POR 10 DIAS", "medication": "icacort", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-03-09 13:56:52.815082
61	381	5	\N	[{"medication": "MINOXIDIL 2,5MG", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA"}, {"brand": null, "id": 126, "instructions": "TOMAR 1 CP VO POR DIA", "medication": "FINASTERIDA 1MG", "purpose": null, "type": "oral"}]	[{"medication": "PIELLUS FORTE", "type": "topical", "instructions": "LAVAR O COURO CABELUDO 1X/DIA"}, {"medication": "KELUAL SQUANORM Kelual S Shampoo anticaspa DUCRAY", "type": "topical", "instructions": "LAVAR O COURO CABELUDO 1X/DIA"}]	\N	dermascribe	2026-03-09 14:14:23.144217
62	383	5	\N	[{"medication": "NEOSIL ATTACK", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA POR 3 MESES"}, {"medication": "MINOXIDIL 2,5MG", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA"}, {"brand": null, "id": 126, "instructions": "TOMAR 1 CP VO POR DIA", "medication": "FINASTERIDA 1MG", "purpose": null, "type": "oral"}]	[]	\N	dermascribe	2026-03-09 19:55:06.107955
63	385	5	\N	[{"medication": "NEOSIL ATTACK", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA POR 3 MESES"}, {"medication": "MINOXIDIL 2,5MG", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA"}, {"brand": null, "id": 126, "instructions": "TOMAR 1 CP VO POR DIA", "medication": "FINASTERIDA 1MG", "purpose": null, "type": "oral"}]	[{"medication": "CAPPY", "type": "topical", "instructions": "APLICAR NO COURO CABELUDO 1X/DIA"}]	\N	dermascribe	2026-03-09 20:09:18.367015
64	396	5	\N	[{"medication": "NEOSIL ATTACK", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA POR 3 MESES"}, {"medication": "MINOXIDIL 2,5MG", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA"}]	[{"medication": "CAPPY", "type": "topical", "instructions": "APLICAR NO COURO CABELUDO 1X/DIA"}]	\N	dermascribe	2026-03-10 18:00:06.634649
65	393	5	\N	[]	[{"brand": "Mantecorp", "id": 47, "instructions": "S\\u00e9rum com retinol para renova\\u00e7\\u00e3o celular e redu\\u00e7\\u00e3o de linhas finas", "medication": "Reviline Retinol S\\u00e9rum", "purpose": null, "type": "topical"}, {"brand": null, "id": 131, "instructions": "aplicar pela manh\\u00e3 antes do protetor", "medication": "Hyaluron-Filler S\\u00e9rum Epigenetic", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-03-10 18:40:34.363972
66	394	5	\N	[{"medication": "terbinafina 250mg", "type": "oral", "instructions": "tomar 1 cp vo por dia por 3 meses"}]	[{"brand": null, "id": 286, "instructions": "aplicar nas unhas 1x/semana ap\\u00f3s lixamento", "medication": "loceryl esmalte", "purpose": null, "type": "topical"}, {"brand": null, "id": 260, "instructions": "aplicar no rosto \\u00c0 noite e retirar pela manh\\u00e3", "medication": "health renew ceaphil", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-03-10 18:52:18.7239
67	392	5	\N	[]	[{"brand": null, "id": 86, "instructions": "aplicar no rosto 2x/dia", "medication": "isdin fusion water", "purpose": null, "type": "topical"}, {"medication": "ISDIN Protetor Solar Facial em bast\\u00e3o Invisible Stick FPS 50-", "type": "topical", "instructions": "aplicar no rosto 2x/dia"}]	\N	dermascribe	2026-03-10 19:09:50.454629
68	395	5	\N	[{"medication": "NEOSIL ATTACK", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA POR 3 MESES"}, {"medication": "MINOXIDIL 2,5MG", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA"}]	[{"medication": "CAPPY", "type": "topical", "instructions": "APLICAR NO COURO CABELUDO 1X/DIA"}]	\N	dermascribe	2026-03-10 19:41:58.455872
69	411	5	\N	[{"medication": "NEOSIL ATTACK", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA POR 3 MESES"}, {"medication": "MINOXIDIL 2,5MG", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA"}, {"brand": null, "id": 126, "instructions": "TOMAR 1 CP VO POR DIA", "medication": "FINASTERIDA 1MG", "purpose": null, "type": "oral"}]	[{"medication": "CAPPY", "type": "topical", "instructions": "APLICAR NO COURO CABELUDO 1X/DIA"}]	\N	dermascribe	2026-03-11 13:21:11.59968
70	398	5	\N	[]	[{"brand": null, "id": 161, "instructions": "APLICAR NO ROSTO 2X/DIA", "medication": "SUNFRESH OIL CONTROL FPS80 NEUTROGENA", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-03-11 13:35:41.84775
71	400	5	\N	[{"medication": "MINOXIDIL 2,5MG", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA"}]	[]	\N	dermascribe	2026-03-11 18:40:22.416544
72	402	5	\N	[{"medication": "MINOXIDIL 2,5MG", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA"}]	[]	\N	dermascribe	2026-03-11 19:22:31.481741
73	404	5	\N	[]	[{"brand": null, "id": 166, "instructions": "Aplicar no rosto \\u00e0 noite e retirar pela manh\\u00e3", "medication": "TARFIC 0,1", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-03-12 12:34:34.975239
74	405	5	\N	[{"medication": "NEOSIL ATTACK", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA POR 3 MESES"}, {"medication": "MINOXIDIL 2,5MG", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA"}, {"brand": null, "id": 126, "instructions": "TOMAR 1 CP VO POR DIA", "medication": "FINASTERIDA 1MG", "purpose": null, "type": "oral"}]	[{"medication": "CAPPY", "type": "topical", "instructions": "APLICAR NO COURO CABELUDO 1X/DIA"}]	\N	dermascribe	2026-03-12 13:51:34.946314
75	408	5	\N	[{"medication": "NEOSIL ATTACK", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA POR 3 MESES"}, {"medication": "MINOXIDIL 2,5MG", "type": "oral", "instructions": "TOMAR 01 CP VO POR DIA"}, {"brand": null, "id": 126, "instructions": "TOMAR 1 CP VO POR DIA", "medication": "FINASTERIDA 1MG", "purpose": null, "type": "oral"}, {"medication": "espironolactona 100mg", "type": "oral", "instructions": "tomar 1 cp vo por dia (uso continuo)"}]	[{"medication": "CAPPY", "type": "topical", "instructions": "APLICAR NO COURO CABELUDO 1X/DIA"}]	\N	dermascribe	2026-03-12 18:56:37.53667
76	419	5	\N	[]	[{"brand": null, "id": 336, "instructions": "APLICAR NAS AREAS DOS OLHOS 1-2X/DIA", "medication": "AGE PROTEON EYE", "purpose": null, "type": "topical"}, {"brand": null, "id": 124, "instructions": "aplicar no rosto \\u00c0 noite e retirar pela manh\\u00e3", "medication": "Esthederm Intensive Pro-Collagen+ - Creme", "purpose": null, "type": "topical"}]	\N	dermascribe	2026-03-12 19:55:35.835999
\.


--
-- Data for Name: procedure; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.procedure (id, name, description, created_at) FROM stdin;
1	LIMELIGHT FACE	\N	\N
2	PROTOCOLO MÃOS(LIMELIGHT + PEARL)	\N	\N
3	PDRN	\N	\N
4	LASER CICATRIZ	\N	\N
5	PEQUENA CIRURGIA	\N	\N
\.


--
-- Data for Name: procedure_follow_up_rule; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.procedure_follow_up_rule (id, procedure_name, follow_up_months, description, created_at) FROM stdin;
\.


--
-- Data for Name: procedure_record; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.procedure_record (id, patient_id, doctor_id, procedure_name, status, planned_date, performed_date, follow_up_due_at, follow_up_status, notes, evolution_id, created_at) FROM stdin;
\.


--
-- Data for Name: surgery; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.surgery (id, date, start_time, end_time, patient_id, patient_name, procedure_id, procedure_name, doctor_id, operating_room_id, status, notes, created_by, updated_by, created_at, updated_at) FROM stdin;
1	2025-12-12	07:30:00	07:45:00	75	DOUGLAS FIOCHIO	\N	TRANSPLANTE CAPILAR	5	1	agendada	\N	5	\N	2025-12-12 18:08:21.042007	2025-12-12 18:08:21.042031
3	2026-01-27	11:00:00	12:00:00	\N	OTAVIO PACHIONE 	\N	EXERESE	5	1	agendada		4	\N	2026-01-26 18:45:32.777904	2026-01-26 18:45:32.777949
4	2026-01-27	07:00:00	08:00:00	\N	THIAGO D AGOSTINHO 	\N	IMPLANTE CAPILAR 	5	1	agendada		4	\N	2026-01-26 18:46:19.914795	2026-01-26 18:46:19.914823
7	2026-02-02	07:15:00	08:15:00	\N	MARIA MADALENA JUNQUEIRA REIS 	\N	MINILIFTH DEEEP PLANE + MORPHEUS 	7	1	agendada		4	\N	2026-02-02 13:49:37.773474	2026-02-02 13:49:37.773501
8	2026-02-02	10:00:00	11:00:00	\N	MIGUEL BIAGI CRUZ SAID 	\N	EXERESE 	7	1	agendada		4	\N	2026-02-02 13:56:22.96371	2026-02-02 13:56:22.963735
9	2026-02-13	07:00:00	08:00:00	\N	MARINA DELDUCA CILINO	\N	MORPHEUS ROSTO COM SEDAÇAO 	5	1	agendada		4	\N	2026-02-10 12:13:03.49454	2026-02-10 12:13:03.494593
10	2026-02-13	09:00:00	10:00:00	\N	DENISE BALDAN	\N	MORPHEUS ROSTO+PREENCHIMENTO LABIAL/SCUPTRA COM SEDAÇAO 	5	1	agendada		4	\N	2026-02-10 12:14:10.939417	2026-02-10 12:14:10.939462
11	2026-02-19	10:00:00	11:00:00	\N	NAIRA CASEMIRO 	\N	PEARL CENTRO CIRURGICO 	5	1	agendada		4	\N	2026-02-13 16:45:02.710754	2026-02-13 16:45:02.710782
12	2026-02-19	07:00:00	08:00:00	\N	FABIO GALVAO SOUZA 	\N	IMPLANTE CAPILAR 	5	1	agendada		4	\N	2026-02-13 16:45:44.139575	2026-02-13 16:45:44.139672
13	2026-02-19	08:30:00	09:30:00	\N	DANIEL DE JESUS BONFIM 	\N	IMPLANTE CAPILAR 	5	1	agendada		4	\N	2026-02-13 16:46:19.190621	2026-02-13 16:46:19.190648
14	2026-02-20	10:30:00	11:30:00	\N	ROCANA CAZON ANGELO 	\N	MORPHEUS ROSTO / LIMELIGTH 	5	1	agendada		4	\N	2026-02-13 16:47:30.046152	2026-02-13 16:47:30.046181
15	2026-02-20	09:00:00	10:00:00	\N	LILIANA BIAGI CRUZ SAID 	\N	MORPHEUS ROSTO/ECSOSOMOS+PREENCHIMENTO	5	1	agendada		4	\N	2026-02-13 16:48:39.528753	2026-02-13 16:48:39.528782
16	2026-03-13	11:00:00	12:00:00	\N	JONAS RICARDO GARDINI 	\N	EXERESE 	5	1	agendada		4	\N	2026-03-11 12:18:20.472139	2026-03-11 12:18:20.472169
17	2026-03-12	08:00:00	09:00:00	\N	CAMILA DE BARROS MEIRELLES 	\N	MORPHEUS 	5	1	agendada		4	\N	2026-03-11 18:39:13.195981	2026-03-11 18:39:13.196012
18	2026-03-12	10:45:00	11:45:00	\N	ANTONIO CIRNE SALGADO	\N	BIOPSIA 	5	1	agendada	PROCEDIMENTO REALIZADO PELA UNIMED 	4	\N	2026-03-11 20:57:04.082025	2026-03-11 20:57:04.082048
19	2026-03-13	12:00:00	13:00:00	\N	ROBERVAL CARVALHO	\N	CAUTERIZAÇAO 	5	1	cancelada		4	4	2026-03-12 19:17:31.196542	2026-03-12 19:52:35.429551
\.


--
-- Data for Name: surgery_evolution; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.surgery_evolution (id, surgery_id, doctor_id, evolution_date, content, created_at, evolution_type, has_necrosis, has_scabs, has_infection, has_follicle_loss, result_rating, needs_another_surgery, has_folliculitis_acute, has_folliculitis_chronic, has_rarefaction, has_local_failure, patient_satisfied, result_within_expected, using_oral_medication, needs_body_hair, needs_touch_up) FROM stdin;
1	1	5	2025-12-02 01:57:56.9143	Sem sinais de necrose\nSem crostas\nSem edema	2025-12-02 01:57:56.914326	general	f	f	f	f	\N	f	f	f	f	f	\N	\N	\N	f	f
3	3	5	2025-12-03 20:06:55.949679	bom resultado com 6 meses passo 1 mes de atibiotico com pustula e espinhas prfundas\n queimo nl qa e qs no couro cabeludo	2025-12-03 20:06:55.949698	general	f	f	f	f	\N	f	f	f	f	f	\N	\N	\N	f	f
4	4	5	2025-12-03 20:10:20.68813	boa evolção otimo resultado com 6 meses	2025-12-03 20:10:20.688156	general	f	f	f	f	\N	f	f	f	f	f	\N	\N	\N	f	f
5	1	5	2025-12-04 20:35:23.426336	1 semana sem crosta sem sinais de necrose\nja libero para exercicio\n\ninicio finasteridae e minoxdil oral que ja usava	2025-12-04 20:35:23.426359	general	f	f	f	f	\N	f	f	f	f	f	\N	\N	\N	f	f
6	6	5	2025-12-05 13:42:21.13173	SEM SINAS DE NECROSE SEM CROSTAS\nUso Oral\nNEOSIL ATTACK\nTOMAR 01 CP VO POR DIA POR 3 MESES\nMINOXIDIL 2,5MG\nTOMAR 01 CP VO POR DIA\nFINASTERIDA 1MG\nTOMAR 1 CP VO POR DIA\nUso Tópico\nCAPPY\nAPLICAR NO COURO CABELUDO 1X/DIA	2025-12-05 13:42:21.131755	general	f	f	f	f	\N	f	f	f	f	f	\N	\N	\N	f	f
7	7	5	2025-12-10 18:36:32.541852	6 meses bom resultado mas falta densidade ainda, passo shampoo anti caspa	2025-12-10 18:36:32.541874	general	f	f	f	f	\N	f	f	f	f	f	\N	\N	\N	f	f
8	11	5	2026-01-21 17:59:01.796363	otimo resultado com 1 ano inicio finasteirda e minoxidil oral 2,5mg \ntiro foto	2026-01-21 17:59:01.796393	general	f	f	f	f	\N	f	f	f	f	f	\N	\N	\N	f	f
9	12	5	2026-01-21 20:22:09.727779	PCTE COM QUEDA DE CABELO GERAL APENAS EM USO DE MINOXIDIL\n PASSO FINASTERIDA SOLICITO EXAMES	2026-01-21 20:22:09.727816	general	f	f	f	f	\N	f	f	f	f	f	\N	\N	\N	f	f
10	13	5	2026-01-23 19:22:46.98243	otimo reusltado com 1 ano\nem uso de minoxdil finsaterida\nainda esta ralo escalpe medio tiro foto mas nao foi colocado	2026-01-23 19:22:46.982455	general	f	f	f	f	\N	f	f	f	f	f	\N	\N	\N	f	f
11	14	5	2026-01-26 18:49:48.709909	TOMAR 1 CP VO POR DIA POR 3 MESES\nFINASTERIDA 1MG\nTOMAR 1 CP VO POR DIA\nMINOXIDIL 2,5 MG\nTOMAR 1 CP VO POR DIA (USO CONTINUO)\n\notimo resutlkado com 1 ano\n tiro foto\n iondico mais 1	2026-01-26 18:49:48.709937	general	f	f	f	f	\N	f	f	f	f	f	\N	\N	\N	f	f
12	15	5	2026-02-03 13:05:44.335255	RECEITUÁRIO\n\nPaciente: MARCO AURELIO BERNARDO\n\nUSO ORAL\nNEOSIL ATTACK\nTOMAR 01 CP VO POR DIA POR 3 MESES\nMINOXIDIL 2,5MG\nTOMAR 01 CP VO POR DIA\nFINASTERIDA 1MG\nTOMAR 1 CP VO POR DIA\nUSO TÓPICO\nCAPPY\nAPLICAR NO COURO CABELUDO 1X/DIA\n\nData: 03/02/2026	2026-02-03 13:05:44.335281	general	f	f	f	f	\N	f	f	f	f	f	\N	\N	\N	f	f
13	16	5	2026-02-03 18:16:32.587243	em uso de finasterida e minoxidil\ntiro foto com 1 ano faz uso de  testo	2026-02-03 18:16:32.58727	general	f	f	f	f	\N	f	f	f	f	f	\N	\N	\N	f	f
14	17	5	2026-02-04 12:59:18.23369	evolução 7 dias:\nsem crostas sem sinais de necrose	2026-02-04 12:59:18.233718	general	f	f	f	f	\N	f	f	f	f	f	\N	\N	\N	f	f
15	20	5	2026-02-11 17:54:00.635838	3 MESES DE CIRURIGIA PACENTE COM FOLICULITE DE REPETICAO NA AREA RECEPETORA\nJA USOU BACTRIN F MELHORA PARCIAL\nINICIO HJ LIMECILINA 30 DIAS	2026-02-11 17:54:00.635868	general	f	f	f	f	\N	f	f	f	f	f	\N	\N	\N	f	f
16	23	5	2026-02-19 20:10:53.164336	otimo resultado com 1 ano\ntiro foto	2026-02-19 20:10:53.164366	general	f	f	f	f	\N	f	f	f	f	f	\N	\N	\N	f	f
17	24	5	2026-02-25 19:40:05.324728	[ACHADOS CIRÚRGICOS - CHECKLIST]\n- Foliculite crônica\n[/ACHADOS CIRÚRGICOS]\n\npaciente tommou bactri 1 semana mas ainda mantem com foliculite\nintroduzo limecilina 12/12 30 diase diprospan	2026-02-25 19:40:05.324756	general	f	f	f	f	\N	f	f	f	f	f	\N	\N	\N	f	f
19	25	5	2026-02-27 17:55:04.917767	[ACHADOS CIRÚRGICOS - CHECKLIST]\n- Rarefação capilar\n[/ACHADOS CIRÚRGICOS]\n\nbom reusltado com 8 meses de cirurgia\n mas sinto ralo como um todo apesar do paciente estar bem sem reclamar\nindico mais uma ciruriga\ninicio finasterida	2026-02-27 17:55:04.917788	general	f	f	f	f	\N	f	f	f	f	f	\N	\N	\N	f	f
21	27	5	2026-02-27 19:45:33.258932	[ACHADOS CIRÚRGICOS - CHECKLIST]\n- Sem achados selecionados\n[/ACHADOS CIRÚRGICOS]\n\npos de 7 dias\nper feito sem crostas sem nada	2026-02-27 19:45:33.258951	general	f	f	f	f	\N	f	f	f	f	f	\N	\N	\N	f	f
22	28	5	2026-03-02 13:15:21.209415	[ACHADOS CIRÚRGICOS - CHECKLIST]\n- Sem achados selecionados\n[/ACHADOS CIRÚRGICOS]\n\notimo resultado com 5 meses	2026-03-02 13:15:21.209444	general	f	f	f	f	\N	f	f	f	f	f	\N	\N	\N	f	f
23	29	5	2026-03-02 20:07:12.422489	[ACHADOS CIRÚRGICOS - CHECKLIST]\n- Falha localizada\n[/ACHADOS CIRÚRGICOS]\n\npaciente feliz mas gostaria de auemntar  adensidade do topete posterior e do escalpe que nem foi colocado\nesta em uso de minzodil com melhora geral do afinamento\nentro com finasterida	2026-03-02 20:07:12.422517	general	f	f	f	f	\N	f	f	f	f	f	\N	\N	\N	f	f
24	30	5	2026-03-04 18:23:10.253125	[ACHADOS CIRÚRGICOS - CHECKLIST]\n- Crostas\n[/ACHADOS CIRÚRGICOS]\n\nRETORNO DE 1 SEMANA	2026-03-04 18:23:10.253152	general	f	f	f	f	\N	f	f	f	f	f	\N	\N	\N	f	f
25	31	5	2026-03-05 14:10:57.31643	[ACHADOS CIRÚRGICOS - CHECKLIST]\n- Crostas\n[/ACHADOS CIRÚRGICOS]\n\nmuita crosta na primeira faixa  esqueda do paciente um pouco de exsudato inicio bactrin f 12/12 5 dias nao tem infeccao	2026-03-05 14:10:57.316461	general	f	f	f	f	\N	f	f	f	f	f	\N	\N	\N	f	f
26	33	5	2026-03-05 19:33:21.589902	[ACHADOS CIRÚRGICOS - CHECKLIST]\n- Sem achados selecionados\n[/ACHADOS CIRÚRGICOS]\n\notimo evolucao com 1 ano	2026-03-05 19:33:21.589928	general	f	f	f	f	\N	f	f	f	f	f	\N	\N	\N	f	f
27	34	5	2026-03-05 19:42:31.865903	[ACHADOS CIRÚRGICOS - CHECKLIST]\n- Sem achados selecionados\n[/ACHADOS CIRÚRGICOS]\n\nperfeito sem muitas crostas\npico temporal perfeito tirei foto j no meu celular	2026-03-05 19:42:31.865934	general	f	f	f	f	\N	f	f	f	f	f	\N	\N	\N	f	f
28	35	5	2026-03-06 13:16:46.369237	[ACHADOS CIRÚRGICOS - CHECKLIST]\n- Sem achados selecionados\n[/ACHADOS CIRÚRGICOS]\n\nretorno 7 dias sem crosta otimo resultado	2026-03-06 13:16:46.36927	general	f	f	f	f	\N	f	f	f	f	f	\N	\N	\N	f	f
29	36	5	2026-03-09 13:25:02.782207	[ACHADOS CIRÚRGICOS - CHECKLIST]\n- Sem achados selecionados\n[/ACHADOS CIRÚRGICOS]\n\n1 ANO DE CIRURGIA TEM INDICAO DA SEGUNDA\nOTIMO RESULTADO	2026-03-09 13:25:02.78223	general	f	f	f	f	\N	f	f	f	f	f	\N	\N	\N	f	f
30	37	5	2026-03-09 14:11:06.082572	[ACHADOS CIRÚRGICOS - CHECKLIST]\n- Sem achados selecionados\n[/ACHADOS CIRÚRGICOS]\n\n1 ANO DE CIRURGIA PROGRAMADO 2 DESDE O COMECO ACHO QUE PRECISA MAIS UMA\n60 COROA E 40 FRONTAL NAO FAZER A HAIRLINE	2026-03-09 14:11:06.082596	general	f	f	f	f	\N	f	f	f	f	f	\N	\N	\N	f	f
31	38	5	2026-03-10 17:16:38.306359	[TIPO DE RETORNO] 7_days\n[CHECKLIST]\n- Crostas\n- Foliculite\n[OBSERVAÇÕES]\nachei com muitas pusstulas porem sem aspecto de infeccao secundaria\ninicio bactrin f\nachei muito eritematoso e epiderme sofrida\ncrostas mais aderidas no centro na primeira faixa	2026-03-10 17:16:38.306377	general	f	f	f	f	\N	f	f	f	f	f	\N	\N	\N	f	f
32	39	5	2026-03-10 18:14:39.729111	[TIPO DE RETORNO] 7_days\n[CHECKLIST]\n- Foliculite\n[OBSERVAÇÕES]\nmuitas pustulas sem crosta\ncabelo afro\ndou bactrin f1212 7dias	2026-03-10 18:14:39.72913	general	f	f	f	f	\N	f	f	f	f	f	\N	\N	\N	f	f
33	40	5	2026-03-11 13:22:17.310449	[TIPO DE RETORNO] 7_days\n[CHECKLIST]\n- Crostas\n[OBSERVAÇÕES]\ncrostas leve na primeira faixa	2026-03-11 13:22:17.310485	general	f	f	f	f	\N	f	f	f	f	f	\N	\N	\N	f	f
34	42	5	2026-03-12 13:50:22.478988	[TIPO DE RETORNO] 7_days\n[OBSERVAÇÕES]\nperfeito com 1 semana	2026-03-12 13:50:22.479013	general	f	f	f	f	\N	f	f	f	f	f	\N	\N	\N	f	f
\.


--
-- Data for Name: tag; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.tag (id, name, color, created_at) FROM stdin;
\.


--
-- Data for Name: transplant_image; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.transplant_image (id, hair_transplant_id, image_type, file_path, description, created_at) FROM stdin;
\.


--
-- Data for Name: transplant_surgery; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.transplant_surgery (id, hair_transplant_id, surgery_date, surgical_planning, complications, created_at) FROM stdin;
\.


--
-- Data for Name: transplant_surgery_record; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.transplant_surgery_record (id, patient_id, doctor_id, surgery_date, surgical_data, observations, created_at, updated_at, surgery_type, status, planning_snapshot, calendar_event_id) FROM stdin;
1	11	5	2025-11-27	4775	60 frontal	2025-12-02 01:24:02.839661	2025-12-02 01:24:02.839686	\N	scheduled	\N	\N
3	30	5	2025-07-02	Médico: Arthur \nEquipe:  Ana, Lavínia, Natália, Aline\nHora da cirurgia: 7h\nTempo de cirurgia:6:41\n\nN Total de Folículo: 3931\nFrente:2165 \nDensidade scketh primeira faixa\n:\nCoroa: 1420\nScalpe: 346\nPenínsula direita: \nPenínsula esquerda:\nFuros: lâmina \nPunch: 0,9\nQuantidade de solução frente:3\nCoroa: 8\nSolução de xilo Frente: 1\n\n\nImplante secundário: não\n\nLD:49(14)700,557\nMD:72(21)1500,1282\nME:72(22)1600,1416\nLE:49(15)750,676\n\nQualidade \nInfiltração (1-3): 2\nSedação (1-3): 2\nSangrando (1-3): 3\nOpções \n* 1 normal\n* ?2 moderado\n* ?3 intenso		2025-12-03 20:04:05.4522	2025-12-03 20:04:05.452237	\N	scheduled	\N	\N
4	28	5	2025-06-17	Data:17/06/2025\nPaciente: Cássio Florêncio Rubio \nMédico:Arthur\nEquipe: Aline, Ana, Lavínia, Natália\nHora da cirurgia: 8h\nTempo de cirurgia: 5h32\nN Total de Folículo: 3421\nFrente: \nDensidade scketh primeira faixa: 82\nCoroa: 3421\nScalpe: \nPenínsula direita:\nPenínsula esquerda:\nFuros: lâmina \nPunch: 0,85\nQuantidade de solução frente:\nCoroa: 5\nSolução de xilo Frente: \n\n\nImplante secundário: não \n\nLE:58(9)500,450\nME:76(18)2400,1357\nMD:76(16)1200,1110\nLD:59(11)659,504\n\n\nQualidade \nInfiltração (1-3): 1\nSedação (1-3): 1\nSangrando (1-3): 2\nOpções \n* 1 normal\n* ?2 moderado\n* ?3 intenso \n\nSolução feita com: \n100 ml SF\n10 ml de xilo\n10 ml de bupi\n1ml adrenalina\n\nComentários: Implante primário, foliculos maioria de 1 e 2 fios, Fios de espessura grosso   e comprimento longo. \n\nMedicações feitas na cirurgia:\nTransamin: sim \nTadalafila: não\nDiprospam : não \nFumante:não\nAntecedente pessoal:nega \n\nOutros: fentanil ev		2025-12-03 20:09:57.864985	2025-12-03 20:09:57.865009	\N	scheduled	\N	\N
5	38	5	2024-11-28	Data: 28/11/2024\nPaciente: Marcelo Eduardo Lamarca\nMédico: Arthur, Filipe, Daniel\nEquipe: RP\nHora da cirurgia:8h\nTempo de cirurgia:6h05\nN Total de Folículo:3.740\nFrente:2555\nCoroa: 700\nScalpe:\nPenínsula direita:170\nPenínsula esquerda:315\nFuros: furador\nPunch: 0,9\nQuantidade de solução frente: 5,5\nCoroa: 6\nSolução de xilo Frente: 1\n\nImplante secundário: Não \n\nLE:  45(15)700,662\nME: 52(21)1100,1048\nMD: 59(26)1550,1500\nLD:  48(14)650,530\n\nQualidade \nInfiltração (0-4): 3\nSedação (0-4): 3\nSangrando (0-4): 2\n\nSolução feita com: \n250 ml SF\n10ml de bupi\n20 ml de xilo\n1 ml adrenalina		2025-12-05 13:23:15.115391	2025-12-05 13:23:15.115414	\N	scheduled	\N	\N
6	39	5	2025-11-28	Data: 28/11/2025\n• Paciente: Hugo Branquinho de Carvalho\n• Unidade: Ribeirão Preto\n• Médico: Dr. Arthur\n• Equipe: Aline, Ana, Lavinia, Natália\n• Hora da cirurgia: 07:00\n• Tempo de cirurgia: 6h\n\nDADOS DA CIRURGIA:\n• Total de folículos: 4052\n\nÁREAS TRATADAS:\n• Frente: 1462\n• Coroa: 2590\n• Scalpe: \n• Península direita: \n• Península esquerda: \n\nRETOQUE: Não\nTIPO DE IMPLANTE: Exclusivo Capilar\n\n=== PROCEDIMENTOS E FERRAMENTAS ===\n• Safira: Não\n• Punch: 0,85x4mm\n\nSOLUÇÕES:\n• Solução frente: 2 seringas de 3ml\n• Solução coroa: 6 seringas de 3ml\n• Solução xilo frente: 1 seringas de 3ml\n\nBLOQUEIO:\n• Bloqueio: Não\n• Seringas de bloqueio: \n• Comentários bloqueio: \n\nIMPLANTE SECUNDÁRIO: Sim\nQUADRANTES (Área/Densidade/Furos/Fios):\n• Q1 (LE): 66cm² | 12.121212121212121 UF/cm² | 800 furos | 751 fios | Taxa quebra: 6.1%\n• Q2 (ME): 94cm² | 14.042553191489361 UF/cm² | 1320 furos | 1278 fios | Taxa quebra: 3.2%\n• Q3 (MD): 93cm² | 17.204301075268816 UF/cm² | 1600 furos | 1458 fios | Taxa quebra: 8.9%\n• Q4 (LD): 80cm² | 8.125 UF/cm² | 650 furos | 572 fios | Taxa quebra: 12.0%\n\n\nAVALIAÇÃO DA QUALIDADE (1=normal, 2=moderado, 3=intenso):\n• Infiltração: 2\n• Sedação: 2\n• Sangramento: 3\n\nMEDICAÇÕES UTILIZADAS:\n• Transamin: Sim\n• Tadalafila: Não\n• Diprospam/Beta 30: Não\n\nHISTÓRICO MÉDICO:\n• Fumante: Não\n• Antecedente pessoal: Nega\n\n\n\nCOMENTÁRIOS GERAIS:\nFios de 1 e 2, espessura grossa e comprimento médio		2025-12-05 13:29:56.139684	2025-12-05 13:29:56.139704	\N	scheduled	\N	\N
7	52	5	2025-05-26	Data: 26/05/2025\nPaciente: Iuri Sverzut Bellesini\nMédico: Dr Arthur \nEquipe:Natália, Aline, Lavínia e Ana \nHora da cirurgia: 7h\nTempo de cirurgia:5h17\nN Total de Folículo: 4376\nFrente:2210\nDensidade scketh primeira faixa:119\nCoroa:1766\nScalpe:210\nPenínsula direita:80\nPenínsula esquerda:110\nFuros: lâmina e Safira \nPunch: 0,85\nQuantidade de solução frente: 3\nCoroa: 7\nSolução de xilo Frente: 1\nXilo com vaso:\n\nImplante secundário: não \n\nLE:67(13)850,800\nME:81(19)1500,1380\nMD:81(19)1500,1433\nLD:64(13)800,763\n\n\nQualidade \nInfiltração (1-3): 1\nSedação (1-3): 1\nSangrando (1-3): 1\nOpções		2025-12-10 18:35:57.921242	2025-12-10 18:35:57.921264	\N	scheduled	\N	\N
8	75	5	2025-12-12	• Data: 12/12/2025\n• Paciente: Douglas  R M Domingos Fiochio \n• Unidade: Ribeirão Preto\n• Médico: Dr. Arthur\n• Equipe: Aline, Ana, Lavinia, Natália\n• Hora da cirurgia: 08:00\n• Tempo de cirurgia: 7h\n\nDADOS DA CIRURGIA:\n• Total de folículos: 4042\n\nÁREAS TRATADAS:\n• Frente: 3277\n• Coroa: \n• Scalpe: \n• Península direita: 365\n• Península esquerda: 400\n\nRETOQUE: Não\nTIPO DE IMPLANTE: Exclusivo Capilar\n\n=== PROCEDIMENTOS E FERRAMENTAS ===\n• Safira: Sim\n• Punch: 0,85x4mm\n\nSOLUÇÕES:\n• Solução frente: 5 seringas de 3ml\n• Solução coroa:  seringas de 3ml\n• Solução xilo frente: 1 seringas de 3ml\n\nBLOQUEIO:\n• Bloqueio: Não\n• Seringas de bloqueio: \n• Comentários bloqueio: \n\nIMPLANTE SECUNDÁRIO: Não\nQUADRANTES (Área/Densidade/Furos/Fios):\n• Q1 (LE): 63cm² | 13.492063492063492 UF/cm² | 850 furos | 807 fios | Taxa quebra: 5.1%\n• Q2 (ME): 80cm² | 19.375 UF/cm² | 1550 furos | 1493 fios | Taxa quebra: 3.7%\n• Q3 (MD): 80cm² | 17.5 UF/cm² | 1400 furos | 1202 fios | Taxa quebra: 14.1%\n• Q4 (LD): 67cm² | 8.955223880597014 UF/cm² | 600 furos | 540 fios | Taxa quebra: 10.0%\n\n\nAVALIAÇÃO DA QUALIDADE (1=normal, 2=moderado, 3=intenso):\n• Infiltração: 1\n• Sedação: 2\n• Sangramento: 3\n\nMEDICAÇÕES UTILIZADAS:\n• Transamin: Sim\n• Tadalafila: Não\n• Diprospam/Beta 30: Não\n\nHISTÓRICO MÉDICO:\n• Fumante: Não\n• Antecedente pessoal: Nega \n\n\n\nCOMENTÁRIOS GERAIS:\nFios de 1,2 médios e grossos		2025-12-12 20:14:05.592679	2025-12-12 20:14:05.592702	\N	scheduled	\N	\N
9	80	5	2025-12-08	DADOS GERAIS:\n• Data: 08/12/2025\n• Paciente: Sérgio Eduardo S Lima \n• Unidade: Ribeirão Preto\n• Médico: Dr. Arthur\n• Equipe: Aline, Ana, Lavinia, Natália\n• Hora da cirurgia: 08:30\n• Tempo de cirurgia: 5h\n\nDADOS DA CIRURGIA:\n• Total de folículos: 3740\n\nÁREAS TRATADAS:\n• Frente: 2620\n• Coroa: 910\n• Scalpe: 210\n• Península direita: 50\n• Península esquerda: 50\n\nRETOQUE: Não\nTIPO DE IMPLANTE: Exclusivo Capilar\n\n=== PROCEDIMENTOS E FERRAMENTAS ===\n• Safira: Não\n• Punch: 0,90x4mm\n\nSOLUÇÕES:\n• Solução frente: 5 seringas de 3ml\n• Solução coroa: 3 seringas de 3ml\n• Solução xilo frente: 1 seringas de 3ml\n\nBLOQUEIO:\n• Bloqueio: Não\n• Seringas de bloqueio: \n• Comentários bloqueio: \n\nIMPLANTE SECUNDÁRIO: Não\nQUADRANTES (Área/Densidade/Furos/Fios):\n• Q1 (LE): 59cm² | 14.40677966101695 UF/cm² | 850 furos | 803 fios | Taxa quebra: 5.5%\n• Q2 (ME): 80cm² | 17.125 UF/cm² | 1370 furos | 1313 fios | Taxa quebra: 4.2%\n• Q3 (MD): 80cm² | 16.25 UF/cm² | 1300 furos | 1013 fios | Taxa quebra: 22.1%\n• Q4 (LD): 56cm² | 12.5 UF/cm² | 700 furos | 611 fios | Taxa quebra: 12.7%\n\n\nAVALIAÇÃO DA QUALIDADE (1=normal, 2=moderado, 3=intenso):\n• Infiltração: 2\n• Sedação: 1\n• Sangramento: 2\n\nMEDICAÇÕES UTILIZADAS:\n• Transamin: Sim\n• Tadalafila: Sim\n• Diprospam/Beta 30: Não\n\nHISTÓRICO MÉDICO:\n• Fumante: Não\n• Antecedente pessoal: Nega \n\n\n\nCOMENTÁRIOS GERAIS:\nFios de 1,2 fino e curto. Usado 1  ampola de transamim na infiltração.		2025-12-15 13:42:46.046439	2025-12-15 13:42:46.046462	\N	scheduled	\N	\N
10	89	5	2025-12-08	DADOS GERAIS:\n• Data: 08/12/2025\n• Paciente: Paulo César Cintra \n• Unidade: Ribeirão Preto\n• Médico: Dr. Arthur\n• Equipe: Aline, Ana, Lavinia, Natália\n• Hora da cirurgia: 07:00\n• Tempo de cirurgia: 6.5h\n\nDADOS DA CIRURGIA:\n• Total de folículos: 4209\n\nÁREAS TRATADAS:\n• Frente: 3025\n• Coroa: 824\n• Scalpe: 360\n• Península direita: 70\n• Península esquerda: 130\n\nRETOQUE: Não\nTIPO DE IMPLANTE: Exclusivo Capilar\n\n=== PROCEDIMENTOS E FERRAMENTAS ===\n• Safira: Não\n• Punch: 0,90x4mm\n\nSOLUÇÕES:\n• Solução frente: 5 seringas de 3ml\n• Solução coroa: 7 seringas de 3ml\n• Solução xilo frente: 1 seringas de 3ml\n\nBLOQUEIO:\n• Bloqueio: Não\n• Seringas de bloqueio: \n• Comentários bloqueio: \n\nIMPLANTE SECUNDÁRIO: Não\nQUADRANTES (Área/Densidade/Furos/Fios):\n• Q1 (LE): 64cm² | 11.71875 UF/cm² | 750 furos | 616 fios | Taxa quebra: 17.9%\n• Q2 (ME): 85cm² | 17.470588235294116 UF/cm² | 1485 furos | 1359 fios | Taxa quebra: 8.5%\n• Q3 (MD): 85cm² | 18.270588235294117 UF/cm² | 1553 furos | 1474 fios | Taxa quebra: 5.1%\n• Q4 (LD): 63cm² | 13.65079365079365 UF/cm² | 860 furos | 760 fios | Taxa quebra: 11.6%\n\n\nAVALIAÇÃO DA QUALIDADE (1=normal, 2=moderado, 3=intenso):\n• Infiltração: 1\n• Sedação: 2\n• Sangramento: 3\n\nMEDICAÇÕES UTILIZADAS:\n• Transamin: Sim\n• Tadalafila: Não\n• Diprospam/Beta 30: Não\n\nHISTÓRICO MÉDICO:\n• Fumante: Não\n• Antecedente pessoal: Nega \n\n\n\nCOMENTÁRIOS GERAIS:\nFios de 1,2 espessura média e comprimento médio utilizado 1 ampola de transamim na solução de infiltração.		2025-12-15 18:34:28.712484	2025-12-15 18:34:28.712508	\N	scheduled	\N	\N
11	102	5	2024-12-05	Data: 04/12/2024\nPaciente: Anderson Moreira Zanon Tenório\nMédico:Arthur, Filipe e Daniel \nEquipe: RP+Ana Paula\nHora da cirurgia:8h\nTempo de cirurgia:5h20\nN Total de Folículo:3731\nFrente:3246\nCoroa:\nScalpe: \nPenínsula direita- 240\nPenínsula esquerda-245\nFuros: furador\nPunch: 0,9\nQuantidade de solução frente: 7\nCoroa:\nSolução de xilo Frente: 1\n\nImplante secundário: não \n\n\nLE:56(13)700,657\nME:67(19)1270,1214\nMD:67(20)1350,1290\nLD:56(12)650,570\n\nQualidade \nInfiltração (0-4): 3\nSedação (0-4): 3\nSangrando (0-4): 3\n\nSolução feita com: \n250 ml SF\n10ml de bupi\n20 ml de xilo\n1 ml adrenalina		2026-01-21 17:58:34.034767	2026-01-21 17:58:34.034795	\N	scheduled	\N	\N
12	108	5	2024-09-18	Data:18/09/2024\nPaciente: William dos Santos\nMédico:Arthur,Filipe e Daniel \nEquipe: RP\nHora da cirurgia: 7:30\nTempo de cirurgia:5h37\nN Total de Folículo:3831\nFrente:2265\nPeninsula D:250\nPeninsula E:251\nCoroa:620\nScalpe:445\nFuros: Furador , Safira\nPunch:  0,85 e 0,85 longo \nQuantidade de solução frente:6\nCoroa:6\nSolução de xilo Frente:1\n\nImplante secundário: não\n\nLE: 56(14)750,542\nME: 81(17)1300,1202\nMD:81(17)1400,1311\nLD: 83(11)900,776\n\nQualidade \nInfiltração (0-4): 3\nSedação (0-4): 3\nSangrando (0-4): 2\n\nSolução feita com: \n  250 ml SF\n 10ml de bupi\n 20 ml de xilo\n1 ml adrenalina\n\nComentários: fios na maioria		2026-01-21 20:21:44.907538	2026-01-21 20:21:44.90757	\N	scheduled	\N	\N
13	120	5	2024-12-09	Data: 09/12/2024\nPaciente:  Allan Ricardo Caruso\nMédico:Arthur, Filipe e Daniel \nEquipe: RP\nHora da cirurgia: 8h\nTempo de cirurgia: 6h50\nN Total de Folículo: 3796\nFrente: 2431\nCoroa:1000\nScalpe: \nPenínsula direita- 160\n\nPenínsula esquerda-115\nFuros: furador\nPunch: 0,85\nQuantidade de solução frente:6,5\nCoroa:3,5\nSolução de xilo Frente: 1\n\nImplante secundário: SIM \n\nLE:53(14)750,703\nME:77(18)1350,1300\nMD:76(17)1300,1045\nLD:48(15)700,658\n\nQualidade \nInfiltração (0-4): 3\nSedação (0-4): 3\nSangrando (0-4): 2\n\nSolução feita com: \n250 ml SF\n10ml de bupi\n20 ml de xilo\n1 ml adrenalina		2026-01-23 19:22:18.726857	2026-01-23 19:22:18.726882	\N	scheduled	\N	\N
14	126	5	2024-11-27	Data: 27/11/2024\nPaciente: Antônio Jacinto Guimarães \nMédico: Arthur, Filipe e Daniel \nEquipe: RP\nHora da cirurgia:8h\nTempo de cirurgia:6h50\nN Total de Folículo: 3881\nFrente: 2530\nCoroa: 901\nScalpe: 450\nPenínsula direita- \nPenínsula esquerda- \nFuros: furador\nPunch: 0,85\nQuantidade de solução frente: 5\nCoroa: 6\nSolução de xilo Frente: 1\n\nImplante secundário: Não \n\nLE: 49(14)750,714\nME:68(20)1300,1235\nMD: 68(20)1300,1279\nLD:  49(14)700,653\n\nQualidade \nInfiltração (0-4): 3\nSedação (0-4): 3\nSangrando (0-4): 2\n\nSolução feita com: \n250 ml SF\n10ml de bupi\n20 ml de xilo\n1 ml adrenalina\n\nComentários: fios na maioria de 1 e 2 espessura fina comprimento médio, sem intercorrências.		2026-01-26 18:48:42.976329	2026-01-26 18:48:42.976357	\N	scheduled	\N	\N
15	118	5	2023-04-28	FUE FRONTAL 70\nE COROA 30		2026-02-03 13:05:25.454684	2026-02-03 13:05:25.454706	\N	scheduled	\N	\N
16	106	5	2025-03-03	Data:31/03/2025\nPaciente:Valdinei Marcos da Costa \nMédico:Arthur \nEquipe:Ana, Aline, Natália, Lavínia \nHora da cirurgia:8h\nTempo de cirurgia: 5h56\nN Total de Folículo: 3722\nFrente: 267\nDensidade scketh primeira faixa: 8,4 | coroa: 59\nCoroa:3455\nScalpe: \nPenínsula direita:\nPenínsula esquerda:\nSafira: não \nPunch:0,85 \nQuantidade de solução frente: 1\nCoroa: 3\nSolução de xilo Frente: 0\n\nImplante secundário: não \n\nLE:55(15)830,700\nME:64(20)1250,1154\nMD:58(18)1200,1106\nLD:56(14)800,762\n\nQualidade \nInfiltração (1-3): 1\nSedação (1-3): 1\nSangrando (1-3): 3\nOpções \n* 1 normal\n* ?2 moderado\n* ?3 intenso \n\nSolução feita com: \n100 ml SF\n10 ml de xilo		2026-02-03 18:15:46.737998	2026-02-03 18:15:46.73802	\N	scheduled	\N	\N
17	171	5	2026-01-28	DADOS GERAIS:\n* Data: 28/01/2026\n* Paciente: Alexandre Vinícius da Silva Pereira \n* Unidade: Ribeirão Preto\n* Médico: Dr. Arthur\n* Equipe: Aline, Ana, Lavinia, Natália\n* Hora da cirurgia: 07:00\n* Tempo de cirurgia: 5h\n\nDADOS DA CIRURGIA:\n* Total de folículos: 4547\n\nÁREAS TRATADAS:\n* Frente: 3670\n* Coroa: 462\n* Scalpe: \n* Península direita: 260\n* Península esquerda: 155\n\nRETOQUE: Não\nTIPO DE IMPLANTE: Exclusivo Capilar\n\n=== PROCEDIMENTOS E FERRAMENTAS ===\n* Safira: Não\n* Punch: 0,85x4mm\n\nSOLUÇÕES:\n* Solução frente: 4 seringas de 3ml\n* Solução coroa: 3 seringas de 3ml\n* Solução xilo frente: 1 seringas de 3ml\n\nBLOQUEIO:\n* Bloqueio: Não\n* Seringas de bloqueio: \n* Comentários bloqueio: \n\nIMPLANTE SECUNDÁRIO: Não\n\n\nQUADRANTES (Área/Densidade/Furos/Fios):\n* Q1 (LE): 56cm² | 15.178571428571429 UF/cm² | 850 furos | 805 fios | Taxa quebra: 5.3%\n* Q2 (ME): 80cm² | 20.125 UF/cm² | 1610 furos | 1540 fios | Taxa quebra: 4.3%\n* Q3 (MD): 80cm² | 18.75 UF/cm² | 1500 furos | 1452 fios | Taxa quebra: 3.2%\n* Q4 (LD): 64cm² | 12.5 UF/cm² | 800 furos | 750 fios | Taxa quebra: 6.2%\n\n\nAVALIAÇÃO DA QUALIDADE (1=normal, 2=moderado, 3=intenso):\n* Infiltração: 1\n* Sedação: 1\n* Sangramento: 2\n\nMEDICAÇÕES UTILIZADAS:\n* Transamin: Não\n* Tadalafila: Não\n* Diprospam/Beta 30: Não\n\nHISTÓRICO MÉDICO:\n* Fumante: Não\n* Antecedente pessoal: Nega\n\n\n\nCOMENTÁRIOS GERAIS:\nFios de 1 e 2, espessura médio e comprimento médio.		2026-02-04 12:58:48.308641	2026-02-04 12:58:48.308666	\N	scheduled	\N	\N
18	184	5	2025-08-31	Data: 31/07/2025\nPaciente: Renan Antunes Conte\nMédico: Arthur \nEquipe: Aline Natália Ana e Lavínia \nHora da cirurgia: 8h\nTempo de cirurgia:7h55\n\nN Total de Folículo: 6350\n\nFrente:2810\n Densidade scketh primeira faixa: 75\nPeninsula D:\nPeninsula E:\nCoroa: 2660\nScalpe: 880\nFuros: lâmina \nPunch: 0,85 cabeca e 1.0/0,9 corpo e barba\nSolução Coroa: 9\nSolução Frente:\nXilo frente:\nImplante primário: Sim \nExtração cabeça \nLD:60(12)750,705\nMD:81(13)1100,1052\nME:81(15)1250,1178\nLE:60(10)600,585\n\nExtração Barba:\n1100,920\n\nExtração peito:\n1450,1114\n\nAbdômen: \n1200,796\nmplantação:\n\nFrente: \nCabelos:2810\nPelos: \n\nCoroa e scalpe \nCabelos:810\nPelos:2730\n\nQualidade \nInfiltração (0-4): 1\nSedação (0-4): 1\nSangrando (0-4): 3\n\nSolução feita com: \nExtração - 250ml de SF, 20 ml de xilo,10 ml de bupi, 01 adrenalina.\n\nFrente: 100ml de SF, 20 ml de xilo, 10 ml de bupi, 01 adrenalina.\n\nComentários:  os folículos do paciente eram na maioria de  1 e 2 com comprimento médio  e espessura médio.\n\n \n\nMedicações feitas na cirurgia \nTransamin: Sim \nTadalafila: nao \nDiprospam: não \nFumante: não \nAntecedente pessoal:Nega \n\nOutros: feito em cirurgia anlodipina, atensina		2026-02-05 19:21:02.7642	2026-02-05 19:21:02.764218	Body Hair	scheduled	\N	\N
19	192	5	2025-05-05	Data: 05/05/2025\nPaciente: Antônio Borges Júnior\nMédico: Arthur \nEquipe: RP\nHora da cirurgia: 07:30 \nTempo de cirurgia: 4h35\nN Total de Folículo: 4030\nFrente: 2845\nDensidade scketh primeira faixa:108\nCoroa: 720\nScalpe: 345\nPenínsula direita: 80\nPenínsula esquerda: 40\nFuros: lâmina \nPunch: 0,85\nQuantidade de solução frente: 6\nCoroa: 7\nSolução de xilo Frente: 1\n\nImplante secundário: Não \n\nLE:49(15)750,720\nME:72(19)1400,1275\nMD:72(19)1380,1320\nLD:52(14)750,715\n\n\nQualidade \nInfiltração (1-3): 1\nSedação (1-3): 1\nSangrando (1-3): 1\nOpções \n* 1 normal\n* ?2 moderado\n* ?3 intenso \n\nSolução feita com: \n100 ml SF\n10 ml de xilo\n10 ml de bupi\n1ml adrenalina\n\nComentários: Implante secu		2026-02-06 13:47:10.211249	2026-02-06 13:47:10.211278	Capilar	scheduled	\N	\N
20	215	5	2025-11-11	DADOS GERAIS:\n* Data: 11/11/2025\n* Paciente: Fernando Henrique Marques Vicente \n* Unidade: Ribeirão Preto\n* Médico: Dr. Arthur\n* Equipe: Aline, Ana, Lavinia, Natália\n* Hora da cirurgia: 07:00\n* Tempo de cirurgia: 5h\n\nDADOS DA CIRURGIA:\n* Total de folículos: 4101\n\nÁREAS TRATADAS:\n* Frente: 3701\n* Coroa: \n* Scalpe: \n* Península direita: 265\n* Península esquerda: 135\n\nRETOQUE: Não\nTIPO DE IMPLANTE: Exclusivo Capilar\n\n=== PROCEDIMENTOS E FERRAMENTAS ===\n* Safira: Não\n* Punch: 0,90x4mm\n\nSOLUÇÕES:\n* Solução frente: 3 seringas de 3ml\n* Solução coroa:  seringas de 3ml\n* Solução xilo frente: 1 seringas de 3ml\n\nBLOQUEIO:\n* Bloqueio: Não\n* Seringas de bloqueio: \n* Comentários bloqueio: \n\nIMPLANTE SECUNDÁRIO: Não\n\n\nQUADRANTES (Área/Densidade/Furos/Fios):\n* Q1 (LE): 48cm² | 14.583333333333334 UF/cm² | 700 furos | 664 fios | Taxa quebra: 5.1%\n* Q2 (ME): 81cm² | 17.901234567901234 UF/cm² | 1450 furos | 1410 fios | Taxa quebra: 2.8%\n* Q3 (MD): 81cm² | 17.901234567901234 UF/cm² | 1450 furos | 1410 fios | Taxa quebra: 2.8%\n* Q4 (LD): 48cm² | 14.583333333333334 UF/cm² | 700 furos | 617 fios | Taxa quebra: 11.9%\n\n\nAVALIAÇÃO DA QUALIDADE (1=normal, 2=moderado, 3=intenso):\n* Infiltração: 1\n* Sedação: 2\n* Sangramento: 1\n\nMEDICAÇÕES UTILIZADAS:\n* Transamin: Não\n* Tadalafila: Não\n* Diprospam/Beta 30: Não\n\nHISTÓRICO MÉDICO:\n* Fumante: Não\n* Antecedente pessoal: Nega\n\n\n\nCOMENTÁRIOS GERAIS:\nFios de 1 e 2 espessura média e comprimento médio.		2026-02-11 17:52:33.032994	2026-02-11 17:52:33.033021		scheduled	\N	\N
21	242	5	2026-02-06	* Data: 06/02/2026\n* Paciente: José Ricardo Minatel\n* Unidade: Ribeirão Preto\n* Médico: Dr. Arthur\n* Equipe: Aline, Ana, Lavinia, Natália\n* Hora da cirurgia: 08:00\n* Tempo de cirurgia: 6h\n\nDADOS DA CIRURGIA:\n* Total de folículos: 4077\n\nÁREAS TRATADAS:\n* Frente: 2980\n* Coroa: 597\n* Scalpe: 500\n* Península direita: \n* Península esquerda: \n\nRETOQUE: Não\nTIPO DE IMPLANTE: Exclusivo Capilar\n\n=== PROCEDIMENTOS E FERRAMENTAS ===\n* Safira: Não\n* Punch: 0,85x4mm\n\nSOLUÇÕES:\n* Solução frente: 2 seringas de 3ml\n* Solução coroa: 3 seringas de 3ml\n* Solução xilo frente: 1 seringas de 3ml\n\nBLOQUEIO:\n* Bloqueio: Não\n* Seringas de bloqueio: \n* Comentários bloqueio: \n\nIMPLANTE SECUNDÁRIO: Não\n\n\nQUADRANTES (Área/Densidade/Furos/Fios):\n* Q1 (LE): 60cm² | 14.166666666666666 UF/cm² | 850 furos | 803 fios | Taxa quebra: 5.5%\n* Q2 (ME): 79cm² | 17.088607594936708 UF/cm² | 1350 furos | 1303 fios | Taxa quebra: 3.5%\n* Q3 (MD): 70cm² | 19.285714285714285 UF/cm² | 1350 furos | 1245 fios | Taxa quebra: 7.8%\n* Q4 (LD): 56cm² | 15 UF/cm² | 840 furos | 726 fios | Taxa quebra: 13.6%\n\n\nAVALIAÇÃO DA QUALIDADE (1=normal, 2=moderado, 3=intenso):\n* Infiltração: 1\n* Sedação: 2\n* Sangramento: 3\n\nMEDICAÇÕES UTILIZADAS:\n* Transamin: Sim\n* Tadalafila: Não\n* Diprospam/Beta 30: Não\n\nHISTÓRICO MÉDICO:\n* Fumante: Não\n* Antecedente pessoal: HAS e diabetico.\n\n\n\nCOMENTÁRIOS GERAIS:\nFios de 1 e 2, espessura média e comprimento médio.		2026-02-13 14:34:02.0693	2026-02-13 14:34:02.069337	Capilar	scheduled	\N	\N
22	249	5	2026-02-11	* Data: 11/02/2026\n* Paciente: Walter Silva Júnior \n* Unidade: Ribeirão Preto\n* Médico: Dr. Arthur\n* Equipe: Aline, Ana, Lavinia, Natália\n* Hora da cirurgia: 08:00\n* Tempo de cirurgia: 6h\n\nDADOS DA CIRURGIA:\n* Total de folículos: 4209\n\nÁREAS TRATADAS:\n* Frente: 3709\n* Coroa: \n* Scalpe: \n* Península direita: 280\n* Península esquerda: 220\n\nRETOQUE: Não\nTIPO DE IMPLANTE: Exclusivo Capilar\n\n=== PROCEDIMENTOS E FERRAMENTAS ===\n* Safira: Sim\n* Punch: 0,85x4mm\n\nSOLUÇÕES:\n* Solução frente: 7 seringas de 3ml\n* Solução coroa:  seringas de 3ml\n* Solução xilo frente: 1 seringas de 3ml\n\nBLOQUEIO:\n* Bloqueio: Não\n* Seringas de bloqueio: \n* Comentários bloqueio: \n\nIMPLANTE SECUNDÁRIO: Não\n\n\nQUADRANTES (Área/Densidade/Furos/Fios):\n* Q1 (LE): 59cm² | 13.898305084745763 UF/cm² | 820 furos | 785 fios | Taxa quebra: 4.3%\n* Q2 (ME): 85cm² | 15.764705882352942 UF/cm² | 1340 furos | 1271 fios | Taxa quebra: 5.1%\n* Q3 (MD): 88cm² | 16.875 UF/cm² | 1485 furos | 1406 fios | Taxa quebra: 5.3%\n* Q4 (LD): 62cm² | 13.709677419354838 UF/cm² | 850 furos | 747 fios | Taxa quebra: 12.1%\n\n\nAVALIAÇÃO DA QUALIDADE (1=normal, 2=moderado, 3=intenso):\n* Infiltração: 1\n* Sedação: 2\n* Sangramento: 3\n\nMEDICAÇÕES UTILIZADAS:\n* Transamin: Sim\n* Tadalafila: Não\n* Diprospam/Beta 30: Não\n\nHISTÓRICO MÉDICO:\n* Fumante: Não\n* Antecedente pessoal: Hás \n\n\n\nCOMENTÁRIOS GERAIS:\nFios de 2 e 3 espessura média e comprimento médio.		2026-02-19 19:52:11.26129	2026-02-19 19:52:11.261319	Capilar	scheduled	\N	\N
23	252	5	2025-02-06	Data:06/02/2025\nPaciente: Gustavo Magalhães dos Santos \nMédico: Arthur e Filipe \nEquipe: RP\nHora da cirurgia:7\nTempo de cirurgia:5h48\nN Total de Folículo:3606\nFrente:2951\nCoroa:\nScalpe:\nPenínsula direita:335\nPenínsula esquerda:320\nFuros:lâmina\nPunch:0,85 \nQuantidade de solução frente:4,5\nCoroa: \nSolução de xilo Frente: 1\n\nImplante secundário: Não \n\nLE:43(13)650,575\nME:76(18)1400,1263\nMD:76(17)1300,1200\nLD:49(14)700,568\n\nQualidade \nInfiltração (1-3): 1\nSedação (1-3): 1\nSangrando (1-3): 1\nOpções \n* 1 sangrando normal\n* ?2 sangramento moderado\n* ?3 sangramento forte durante tempo todo\n\nSolução feita com: \n250 ml SF		2026-02-19 20:08:25.914658	2026-02-19 20:08:25.914686		scheduled	\N	\N
24	278	5	2025-11-13	Data: 13/11/2025\n• Paciente: Márcio Luís Martins \n• Unidade: Ribeirão Preto\n• Médico: Dr. Arthur\n• Equipe: Freelancer 1: Dani Curti, Ana, Lavinia, Natália\n• Hora da cirurgia: 08:00\n• Tempo de cirurgia: 6h\n\nDADOS DA CIRURGIA:\n• Total de folículos: 3526\n\nÁREAS TRATADAS:\n• Frente: 1621\n• Coroa: 1705\n• Scalpe: 200\n• Península direita: \n• Península esquerda: \n\nRETOQUE: Não\nTIPO DE IMPLANTE: \n\n=== PROCEDIMENTOS E FERRAMENTAS ===\n• Safira: Não\n• Punch: 0,90x4mm\n\nSOLUÇÕES:\n• Solução frente: 4 seringas de 3ml\n• Solução coroa: 5 seringas de 3ml\n\nBLOQUEIO:\n• Bloqueio: Não\n• Seringas de bloqueio: \n• Comentários bloqueio: \n\nIMPLANTE SECUNDÁRIO: Sim\n\n\nQUADRANTES (Área/Densidade/Furos/Fios):\n• Q1 (LE): 68cm² | 11.029411764705882 UF/cm² | 750 furos | 664 fios | Taxa quebra: 11.5%\n• Q2 (ME): 76cm² | 17.105263157894736 UF/cm² | 1300 furos | 1207 fios | Taxa quebra: 7.2%\n• Q3 (MD): 76cm² | 14.473684210526315 UF/cm² | 1100 furos | 954 fios | Taxa quebra: 13.3%\n• Q4 (LD): 68cm² | 11.764705882352942 UF/cm² | 800 furos | 701 fios | Taxa quebra: 12.4%\n\n\nAVALIAÇÃO DA QUALIDADE (1=normal, 2=moderado, 3=intenso):\n• Infiltração: 1\n• Sedação: 1\n• Sangramento: 1\n\nMEDICAÇÕES UTILIZADAS:\n• Transamin: Não\n• Tadalafila: Não\n• Diprospam/Beta 30: Não\n\nHISTÓRICO MÉDICO:\n• Fumante: Não\n• Antecedente pessoal: Nega		2026-02-25 19:39:14.979537	2026-02-25 19:39:14.979562	Capilar	scheduled	\N	\N
25	296	5	2025-06-16	ata:16/06/2025\nPaciente: Anderson Silveira \nMédico:Arthur \nEquipe: Aline, Ana, Lavínia, Natália\nHora da cirurgia: 8h\nTempo de cirurgia: 6h31\nN Total de Folículo: :4013\nFrente: 3598\nDensidade scketh primeira faixa: 75\nCoroa: 215\nScalpe: \nPenínsula direita:150\nPenínsula esquerda:150\nFuros: lâmina \nPunch: 0,90 longo\nQuantidade de solução frente:5,5\nCoroa: 2,5\nSolução de xilo Frente: 1\n\n\nImplante secundário: não \n\nLE:64(12)750,540\nME:84(20)1650,1470\nMD:84(20)1680,1478\nLD:64(12)750,535\nQualidade \nInfiltração (1-3): 1\nSedação (1-3): 2\nSangrando (1-3): 3\nOpções \n* 1 normal\n* ?2 moderado\n* ?3 intenso \n\nSolução feita com: \n100 ml SF\n10 ml de xilo\n10 ml de bupi\n1ml adrenalina\n\nComentários: Implante primário, foliculos maioria de 1 e 2 fios, Fios de espessura grossa  e comprimento longo . \n\nMedicações feitas na cirurgia:\nTransamin: sim \nTadalafila: não\nDiprospam : não \nFumante:não\nAntecedente pessoal:nega \n\nOutros:		2026-02-27 14:12:52.217899	2026-02-27 14:12:52.217921	Capilar	scheduled	\N	\N
26	296	5	2025-06-16	ata:16/06/2025\nPaciente: Anderson Silveira \nMédico:Arthur \nEquipe: Aline, Ana, Lavínia, Natália\nHora da cirurgia: 8h\nTempo de cirurgia: 6h31\nN Total de Folículo: :4013\nFrente: 3598\nDensidade scketh primeira faixa: 75\nCoroa: 215\nScalpe: \nPenínsula direita:150\nPenínsula esquerda:150\nFuros: lâmina \nPunch: 0,90 longo\nQuantidade de solução frente:5,5\nCoroa: 2,5\nSolução de xilo Frente: 1\n\n\nImplante secundário: não \n\nLE:64(12)750,540\nME:84(20)1650,1470\nMD:84(20)1680,1478\nLD:64(12)750,535\nQualidade \nInfiltração (1-3): 1\nSedação (1-3): 2\nSangrando (1-3): 3\nOpções \n* 1 normal\n* ?2 moderado\n* ?3 intenso \n\nSolução feita com: \n100 ml SF\n10 ml de xilo\n10 ml de bupi\n1ml adrenalina\n\nComentários: Implante primário, foliculos maioria de 1 e 2 fios, Fios de espessura grossa  e comprimento longo . \n\nMedicações feitas na cirurgia:\nTransamin: sim \nTadalafila: não\nDiprospam : não \nFumante:não\nAntecedente pessoal:nega \n\nOutros:		2026-02-27 17:54:25.75229	2026-02-27 17:54:25.752309		scheduled	\N	\N
27	303	5	2026-02-19	ADOS GERAIS:\n* Data: 19/02/2026\n* Paciente: Fabiano Galvão Sousa\n* Unidade: Ribeirão Preto\n* Médico: Dr. Arthur\n* Equipe: Aline, Ana, Lavinia, Natália\n* Hora da cirurgia: 07:00\n* Tempo de cirurgia: 5.5h\n\nDADOS DA CIRURGIA:\n* Total de folículos: 4119\n\nÁREAS TRATADAS:\n* Frente: 2589\n* Coroa: 1480\n* Scalpe: \n* Península direita: \n* Península esquerda: \n\nRETOQUE: Não\nTIPO DE IMPLANTE: Exclusivo Capilar\n\n=== PROCEDIMENTOS E FERRAMENTAS ===\n* Safira: Não\n* Punch: 0,90x4mm\n\nSOLUÇÕES:\n* Solução frente: 3 seringas de 3ml\n* Solução coroa: 3 seringas de 3ml\n* Solução xilo frente: 1 seringas de 3ml\n\nBLOQUEIO:\n* Bloqueio: Não\n* Seringas de bloqueio: \n* Comentários bloqueio: \n\nIMPLANTE SECUNDÁRIO: Não\n\n\nQUADRANTES (Área/Densidade/Furos/Fios):\n* Q1 (LE): 52cm² | 14.423076923076923 UF/cm² | 750 furos | 680 fios | Taxa quebra: 9.3%\n* Q2 (ME): 76cm² | 19.210526315789473 UF/cm² | 1460 furos | 1340 fios | Taxa quebra: 8.2%\n* Q3 (MD): 76cm² | 19.07894736842105 UF/cm² | 1450 furos | 1312 fios | Taxa quebra: 9.5%\n* Q4 (LD): 56cm² | 15.178571428571429 UF/cm² | 850 furos | 787 fios | Taxa quebra: 7.4%\n\n\nAVALIAÇÃO DA QUALIDADE (1=normal, 2=moderado, 3=intenso):\n* Infiltração: 2\n* Sedação: 2\n* Sangramento: 2\n\nMEDICAÇÕES UTILIZADAS:\n* Transamin: Não\n* Tadalafila: Não\n* Diprospam/Beta 30: Não\n\nHISTÓRICO MÉDICO:\n* Fumante: Não\n* Antecedente pessoal: Nega\n\n\n\nCOMENTÁRIOS GERAIS:\nFios de 2 e 3, espessura grossa e comprimento médio.		2026-02-27 19:44:40.198838	2026-02-27 19:44:40.198857		scheduled	\N	\N
28	310	5	2025-09-17	DADOS GERAIS:\n• Data: 17/09/2025\n• Paciente: Rafael Luís Spina\n• Unidade: Ribeirão Preto\n• Médico: Dr. Arthur\n• Equipe: Aline, Ana, Lavinia, Natália\n• Hora da cirurgia: 08:00\n• Tempo de cirurgia: 5h\n\nDADOS DA CIRURGIA:\n• Total de folículos: 4322\n\nÁREAS TRATADAS:\n• Frente: 3912\n• Coroa: \n• Scalpe: \n• Península direita: 220\n• Península esquerda: 190\n\nDENSIDADE E MEDIDAS:\n• Densidade Scketh: 70\n\nINSTRUMENTOS:\n• Safira: Não\n• Punch: 0,85x4mm\n\nSOLUÇÕES:\n• Solução frente: 6 seringas de 3ml\n• Solução coroa:  seringas de 3ml\n• Solução xilo frente: 1 seringas de 3ml\n\nBLOQUEIO:\n• Bloqueio: Não\n• Seringas de bloqueio: \n• Comentários bloqueio: \nIMPLANTE SECUNDÁRIO: Não\n\n\nQUADRANTES (Área/Densidade/Furos/Fios):\n• Q1 (LE): 56cm² | 15.178571428571429 UF/cm² | 850 furos | 770 fios | Taxa quebra: 9.4%\n• Q2 (ME): 81cm² | 18.51851851851852 UF/cm² | 1500 furos | 1485 fios | Taxa quebra: 1.0%\n• Q3 (MD): 81cm² | 17.28395061728395 UF/cm² | 1400 furos | 1331 fios | Taxa quebra: 4.9%\n• Q4 (LD): 63cm² | 14.285714285714286 UF/cm² | 900 furos | 736 fios | Taxa quebra: 18.2%\n\n\nAVALIAÇÃO DA QUALIDADE (1=normal, 2=moderado, 3=intenso):\n• Infiltração: 1\n• Sedação: 2\n• Sangramento: 2\n\nMEDICAÇÕES UTILIZADAS:\n• Transamin: Não\n• Tadalafila: Não\n• Diprospam/Beta 30: Não\n\nHISTÓRICO MÉDICO:\n• Fumante: Não\n• Antecedente pessoal: Hipertenso \n\n\n\nCOMENTÁRIOS GERAIS:\nFios de 1 e 2 médios e grossos		2026-03-02 13:09:18.104634	2026-03-02 13:09:18.104662		scheduled	\N	\N
29	318	5	2024-09-10	Data:10/09/2024\nPaciente: William Kleber da Silva \nMédico:Arthur,Filipe e Daniel\nEquipe: RP\nHora da cirurgia: 8h00\nTempo de cirurgia: 5h30\nN Total de Folículo: 3550\nFrente:2840\nPeninsula D:205\nPeninsula E:205\nCoroa: 300\nScalpe: \nFuros: Furador , Safira \nPunch:  0,85\nQuantidade de solução frente:6,5\nCoroa: 2\nSolução de xilo Frente: 1\n\nImplante secundário: Não \n\nLE:54(14)750,726\nME: 72(17)1200,1187\nMD: 74(16)1200,1140\nLD: 60(9)550,497\n\nQualidade \nInfiltração (0-4): 3\nSedação (0-4): 3\nSangrando (0-4): 2\n\nSolução feita com: \n  250 ml SF\n 10ml de bupi\n 20 ml de xilo\n1 ml adrenalina\n\nComentários: fios na		2026-03-02 19:59:54.985894	2026-03-02 19:59:54.985921	Capilar	scheduled	\N	\N
30	343	5	2026-02-25	* Data: 25/02/2026\n* Paciente: Guilherme Griffo\n* Unidade: Ribeirão Preto\n* Médico: Dr. Arthur\n* Equipe: Freelancer 1: Thamara Maciel, Aline, Ana, Lavinia\n* Hora da cirurgia: 08:00\n* Tempo de cirurgia: 5h\n\nDADOS DA CIRURGIA:\n* Total de folículos: 4220\n\nÁREAS TRATADAS:\n* Frente: 3270\n* Coroa: 700\n* Scalpe: 250\n* Península direita: \n* Península esquerda: \n\nRETOQUE: Não\nTIPO DE IMPLANTE: Exclusivo Capilar\n\n=== PROCEDIMENTOS E FERRAMENTAS ===\n* Safira: Não\n* Punch: 0,85x4mm\n\nSOLUÇÕES:\n* Solução frente: 2 seringas de 3ml\n* Solução coroa: 7 seringas de 3ml\n* Solução xilo frente: 1 seringas de 3ml\n\nBLOQUEIO:\n* Bloqueio: Não\n* Seringas de bloqueio: \n* Comentários bloqueio: \n\nIMPLANTE SECUNDÁRIO: Não\n\n\nQUADRANTES (Área/Densidade/Furos/Fios):\n* Q1 (LE): 59cm² | 14.40677966101695 UF/cm² | 850 furos | 746 fios | Taxa quebra: 12.2%\n* Q2 (ME): 76cm² | 18.42105263157895 UF/cm² | 1400 furos | 1300 fios | Taxa quebra: 7.1%\n* Q3 (MD): 72cm² | 20.27777777777778 UF/cm² | 1460 furos | 1380 fios | Taxa quebra: 5.5%\n* Q4 (LD): 58cm² | 13.96551724137931 UF/cm² | 810 furos | 794 fios | Taxa quebra: 2.0%\n\n\nAVALIAÇÃO DA QUALIDADE (1=normal, 2=moderado, 3=intenso):\n* Infiltração: 1\n* Sedação: 1\n* Sangramento: 1\n\nMEDICAÇÕES UTILIZADAS:\n* Transamin: Não\n* Tadalafila: Não\n* Diprospam/Beta 30: Não\n\nHISTÓRICO MÉDICO:\n* Fumante: Não\n* Antecedente pessoal: Nega \n\n\n\nCOMENTÁRIOS GERAIS:\nFios de 1 e 2, espessura média e comprimento médio.		2026-03-04 18:22:46.693324	2026-03-04 18:22:46.693351		scheduled	\N	\N
31	360	5	2026-02-26	DADOS GERAIS:\n* Data: 26/02/2026\n* Paciente: Cleber Roberto violin \n* Unidade: Ribeirão Preto\n* Médico: Dr. Arthur\n* Equipe: Freelancer 1: Thamara Maciel, Aline, Ana, Lavinia\n* Hora da cirurgia: 08:00\n* Tempo de cirurgia: 5:44\n\nDADOS DA CIRURGIA:\n* Total de folículos: 4258\n\nÁREAS TRATADAS:\n* Frente: 3013\n* Coroa: 785\n* Scalpe: 460\n* Península direita: \n* Península esquerda: \n\nRETOQUE: Não\nTIPO DE IMPLANTE: Exclusivo Capilar\n\n=== PROCEDIMENTOS E FERRAMENTAS ===\n* Safira: Não\n* Punch: 0,85x5mm\n\nSOLUÇÕES:\n* Solução frente: 2 seringas de 3ml\n* Solução coroa:  seringas de 3ml\n* Solução xilo frente:  seringas de 3ml\n\nBLOQUEIO:\n* Bloqueio: Não\n* Seringas de bloqueio: \n* Comentários bloqueio: \n\nIMPLANTE SECUNDÁRIO: Não\n\n\nQUADRANTES (Área/Densidade/Furos/Fios):\n* Q1 (LE): 66cm² | 12.878787878787879 UF/cm² | 850 furos | 785 fios | Taxa quebra: 7.6%\n* Q2 (ME): 88cm² | 15.681818181818182 UF/cm² | 1380 furos | 1340 fios | Taxa quebra: 2.9%\n* Q3 (MD): 88cm² | 17.954545454545453 UF/cm² | 1580 furos | 1490 fios | Taxa quebra: 5.7%\n* Q4 (LD): 68cm² | 10 UF/cm² | 680 furos | 643 fios | Taxa quebra: 5.4%\n\n\nAVALIAÇÃO DA QUALIDADE (1=normal, 2=moderado, 3=intenso):\n* Infiltração: 2\n* Sedação: 2\n* Sangramento: 3\n\nMEDICAÇÕES UTILIZADAS:\n* Transamin: Sim\n* Tadalafila: Sim\n* Diprospam/Beta 30: Não\n\nHISTÓRICO MÉDICO:\n* Fumante: Não\n* Antecedente pessoal: \n\n\n\nCOMENTÁRIOS GERAIS:\nFios de 2 e 3 , curto e fino		2026-03-05 14:10:14.574316	2026-03-05 14:10:14.574424	Capilar	scheduled	\N	\N
32	366	5	2025-05-12	Data: 12/02/25\nPaciente:  José Samuel de Grande\nMédico:Arthur, Filipe\nEquipe:  RP\nHora da cirurgia: 8h\nTempo de cirurgia: 5h50\nN Total de Folículo: 4.805\nFrente: 3284\nPeninsula D: \nPeninsula E:\nCoroa: 1210\nScalpe: 321\nFuros: lamina\nPunch: 0,85\nSolução Coroa: 7\nSolução de xilo Frente: 1\nSolução frente:6\nImplante primário \nExtração cabeça \n\nLD:48(13)630,600\nMD:63(19)1200,1130\nME:63(17)1100,1050\nLE:45(15)700,652\n\nExtração Barba:\n950/810\n\nExtração tórax:\n940/721\n\nAbdômen:\n\n\nImplantação:\n\nFrente \nCabelos:3274\nPelos:-\n\nCoroa \nCabelos:-\nPelos:1531\n\nQualidade \nnfiltração (1,2,3) 1\nSedação (1,2,3) 2\nSangrando (1,2,3)2\n\nSolução feita com: \nExtração - 250ml de SF, 20 ml de xilo,10 ml de bupi, 01 adrenalina.\n\nFrente: 100ml de SF, 10ml de xilo, 10 ml de bupi, 1/3 adrenalina.\n\nComentários:  os folículos do paciente eram na maioria de 1 e 2, com comprimento medio e espessura fina.\n\n-Pelos da barba com fios (1 ) médio e curto\nPelos do peito com fios (1 e 2) finos e médios\n\n\n\nMedicações feitas na cirurgia:\nTransamin ? Sim 3 ampolas \nTadalafila: não\nDiprospam: não\nFumante: não\nAntecedente pessoal: nega \n\nOutros \nAnlodipino \nTransamin:		2026-03-05 19:32:11.012375	2026-03-05 19:32:11.012402	Body Hair	scheduled	\N	\N
33	366	5	2025-02-12	Data: 12/02/25\nPaciente:  José Samuel de Grande\nMédico:Arthur, Filipe\nEquipe:  RP\nHora da cirurgia: 8h\nTempo de cirurgia: 5h50\nN Total de Folículo: 4.805\nFrente: 3284\nPeninsula D: \nPeninsula E:\nCoroa: 1210\nScalpe: 321\nFuros: lamina\nPunch: 0,85\nSolução Coroa: 7\nSolução de xilo Frente: 1\nSolução frente:6\nImplante primário \nExtração cabeça \n\nLD:48(13)630,600\nMD:63(19)1200,1130\nME:63(17)1100,1050\nLE:45(15)700,652\n\nExtração Barba:\n950/810\n\nExtração tórax:\n940/721\n\nAbdômen:\n\n\nImplantação:\n\nFrente \nCabelos:3274\nPelos:-\n\nCoroa \nCabelos:-\nPelos:1531\n\nQualidade \nnfiltração (1,2,3) 1\nSedação (1,2,3) 2\nSangrando (1,2,3)2\n\nSolução feita com: \nExtração - 250ml de SF, 20 ml de xilo,10 ml de bupi, 01 adrenalina.\n\nFrente: 100ml de SF, 10ml de xilo, 10 ml de bupi, 1/3 adrenalina.\n\nComentários:  os folículos do paciente eram na maioria de 1 e 2, com comprimento medio e espessura fina.\n\n-Pelos da barba com fios (1 ) médio e curto\nPelos do peito com fios (1 e 2) finos e médios\n\n\n\nMedicações feitas na cirurgia:\nTransamin ? Sim 3 ampolas \nTadalafila: não\nDiprospam: não\nFumante: não\nAntecedente pessoal: nega \n\nOutros \nAnlodipino \nTransamin:		2026-03-05 19:32:58.861457	2026-03-05 19:32:58.861482		scheduled	\N	\N
34	368	5	2026-02-26	* Data: 26/02/2026\n* Paciente: Ernane Donizete Lucas Barbosa \n* Unidade: Ribeirão Preto\n* Médico: Dr. Arthur\n* Equipe: Freelancer 1: Thamara Maciel, Aline, Ana, Lavinia\n* Hora da cirurgia: 08:00\n* Tempo de cirurgia: 6h\n\nDADOS DA CIRURGIA:\n* Total de folículos: 3531\n\nÁREAS TRATADAS:\n* Frente: 861\n* Coroa: 1640\n* Scalpe: 40\n* Península direita: 550\n* Península esquerda: 470\n\nRETOQUE: Não\nTIPO DE IMPLANTE: Exclusivo Capilar\n\n=== PROCEDIMENTOS E FERRAMENTAS ===\n* Safira: Não\n* Punch: 0,85x4mm\n\nSOLUÇÕES:\n* Solução frente: 3 seringas de 3ml\n* Solução coroa: 3 seringas de 3ml\n* Solução xilo frente: 1 seringas de 3ml\n\nBLOQUEIO:\n* Bloqueio: Não\n* Seringas de bloqueio: \n* Comentários bloqueio: \n\nIMPLANTE SECUNDÁRIO: Não\n\n\nQUADRANTES (Área/Densidade/Furos/Fios):\n* Q1 (LE): 55cm² | 12.727272727272727 UF/cm² | 700 furos | 512 fios | Taxa quebra: 26.9%\n* Q2 (ME): 78cm² | 17.94871794871795 UF/cm² | 1400 furos | 1235 fios | Taxa quebra: 11.8%\n* Q3 (MD): 82cm² | 17.073170731707318 UF/cm² | 1400 furos | 1102 fios | Taxa quebra: 21.3%\n* Q4 (LD): 63cm² | 12.698412698412698 UF/cm² | 800 furos | 682 fios | Taxa quebra: 14.8%\n\n\nAVALIAÇÃO DA QUALIDADE (1=normal, 2=moderado, 3=intenso):\n* Infiltração: 2\n* Sedação: 2\n* Sangramento: 2\n\nMEDICAÇÕES UTILIZADAS:\n* Transamin: Não\n* Tadalafila: Não\n* Diprospam/Beta 30: Não\n\nHISTÓRICO MÉDICO:\n* Fumante: Não\n* Antecedente pessoal: Nega \n\n\n\nCOMENTÁRIOS GERAIS:\nFios de 1 e 2 espessura média e comprimento curto.		2026-03-05 19:42:00.934677	2026-03-05 19:42:00.934717	Capilar	scheduled	\N	\N
35	377	5	2026-02-27	* Data: 27/02/2026\n* Paciente: Felipe Rangel\n* Unidade: Ribeirão Preto\n* Médico: Dr. Arthur\n* Equipe: Freelancer 1: Thamara Maciel, Aline, Ana, Lavinia\n* Hora da cirurgia: 08:00\n* Tempo de cirurgia: 6.5h\n\nDADOS DA CIRURGIA:\n* Total de folículos: 4263\n\nÁREAS TRATADAS:\n* Frente: 3948\n* Coroa: \n* Scalpe: \n* Península direita: 150\n* Península esquerda: 165\n\nRETOQUE: Não\nTIPO DE IMPLANTE: Exclusivo Capilar\n\n=== PROCEDIMENTOS E FERRAMENTAS ===\n* Safira: Não\n* Punch: 0,85x4mm\n\nSOLUÇÕES:\n* Solução frente: 6 seringas de 3ml\n* Solução coroa:  seringas de 3ml\n* Solução xilo frente: 1 seringas de 3ml\n\nBLOQUEIO:\n* Bloqueio: Não\n* Seringas de bloqueio: \n* Comentários bloqueio: \n\nIMPLANTE SECUNDÁRIO: Não\n\n\nQUADRANTES (Área/Densidade/Furos/Fios):\n* Q1 (LE): 58cm² | 15.517241379310345 UF/cm² | 900 furos | 822 fios | Taxa quebra: 8.7%\n* Q2 (ME): 83cm² | 16.867469879518072 UF/cm² | 1400 furos | 1317 fios | Taxa quebra: 5.9%\n* Q3 (MD): 83cm² | 19.096385542168676 UF/cm² | 1585 furos | 1479 fios | Taxa quebra: 6.7%\n* Q4 (LD): 56cm² | 12.5 UF/cm² | 700 furos | 645 fios | Taxa quebra: 7.9%\n\n\nAVALIAÇÃO DA QUALIDADE (1=normal, 2=moderado, 3=intenso):\n* Infiltração: 3\n* Sedação: 3\n* Sangramento: 3\n\nMEDICAÇÕES UTILIZADAS:\n* Transamin: Sim\n* Tadalafila: Não\n* Diprospam/Beta 30: Não\n\nHISTÓRICO MÉDICO:\n* Fumante: Não\n* Antecedente pessoal: Nega\n\n\n\nCOMENTÁRIOS GERAIS:\nFios de 1 e 2, espessura fina e comprimento médio.		2026-03-06 13:16:20.768977	2026-03-06 13:16:20.768998	Capilar	scheduled	\N	\N
36	379	5	2025-02-18	Data:18/02/2025\nPaciente: Renato César Stella\nMédico: Arthur\nEquipe:RP\nHora da cirurgia: 8h\nTempo de cirurgia: 5h31\nN Total de Folículo:3306\nFrente:2250\nDensidade scketh primeira faixa: 86,5\nCoroa:756\nScalpe:300\nPenínsula direita:200\nPenínsula esquerda:170\nSafira: Não \nPunch:0,85 e 0,9\nQuantidade de solução frente:4,5\nCoroa: 6\nSolução de xilo Frente: 1\n\nImplante secundário: não\n\nLE:49(14)799,605\nME:69(18)1100,1027\nMD:56(20)1100,1019\nLD:45(16)700,655\n\nQualidade \nInfiltração (1-3): 1\nSedação (1-3): 2\nSangrando (1-3):2\nOpções \n* 1 normal\n* ?2 moderado\n* ?3 intenso \n\nSolução feita com:		2026-03-09 13:24:18.71512	2026-03-09 13:24:18.715143	Capilar	scheduled	\N	\N
37	381	5	2025-02-17	3700\n1600 frontal		2026-03-09 14:10:17.301052	2026-03-09 14:10:17.301074	Capilar	scheduled	\N	\N
38	385	5	2026-02-26	* Data: 26/02/2026\n* Paciente: Gabriel Danezzi\n* Unidade: Ribeirão Preto\n* Médico: Dr. Arthur\n* Equipe: Aline, Ana, Lavinia, Natália\n* Hora da cirurgia: 08:00\n* Tempo de cirurgia: 6.5h\n\nDADOS DA CIRURGIA:\n* Total de folículos: 4345\n\nÁREAS TRATADAS:\n* Frente: 3135\n* Coroa: 950\n* Scalpe: 260\n* Península direita: \n* Península esquerda: \n\nRETOQUE: Não\nTIPO DE IMPLANTE: Exclusivo Capilar\n\n=== PROCEDIMENTOS E FERRAMENTAS ===\n* Safira: Não\n* Punch: 0,85x5mm\n\nSOLUÇÕES:\n* Solução frente: 5 seringas de 3ml\n* Solução coroa: 4 seringas de 3ml\n* Solução xilo frente: 1 seringas de 3ml\n\nBLOQUEIO:\n* Bloqueio: Não\n* Seringas de bloqueio: \n* Comentários bloqueio: \n\nIMPLANTE SECUNDÁRIO: Não\n\n\nQUADRANTES (Área/Densidade/Furos/Fios):\n* Q1 (LE): 56cm² | 15.178571428571429 UF/cm² | 850 furos | 796 fios | Taxa quebra: 6.4%\n* Q2 (ME): 85cm² | 17.647058823529413 UF/cm² | 1500 furos | 1468 fios | Taxa quebra: 2.1%\n* Q3 (MD): 81cm² | 17.901234567901234 UF/cm² | 1450 furos | 1244 fios | Taxa quebra: 14.2%\n* Q4 (LD): 60cm² | 15 UF/cm² | 900 furos | 837 fios | Taxa quebra: 7.0%\n\n\nAVALIAÇÃO DA QUALIDADE (1=normal, 2=moderado, 3=intenso):\n* Infiltração: 1\n* Sedação: 1\n* Sangramento: 3\n\nMEDICAÇÕES UTILIZADAS:\n* Transamin: Sim\n* Tadalafila: Não\n* Diprospam/Beta 30: Não\n\nHISTÓRICO MÉDICO:\n* Fumante: Não\n* Antecedente pessoal: Nega \n\n\n\nCOMENTÁRIOS GERAIS:\nFios de 1 e 2 médio e longo		2026-03-10 12:31:56.665447	2026-03-10 12:31:56.665472	Capilar	scheduled	\N	\N
39	396	5	2026-03-03	* Data: 03/03/2026\n* Paciente: Rosado de Souza \n* Unidade: Ribeirão Preto\n* Médico: Dr. Arthur\n* Equipe: Aline, Ana, Lavinia, Natália\n* Hora da cirurgia: 08:00\n* Tempo de cirurgia: 6h\n\nDADOS DA CIRURGIA:\n* Total de folículos: 4002\n\nÁREAS TRATADAS:\n* Frente: 3402\n* Coroa: 600\n* Scalpe: \n* Península direita: 160\n* Península esquerda: 125\n\nRETOQUE: Não\nTIPO DE IMPLANTE: Exclusivo Capilar\n\n=== PROCEDIMENTOS E FERRAMENTAS ===\n* Safira: Não\n* Punch: 0,90x4mm\n\nSOLUÇÕES:\n* Solução frente: 4 seringas de 3ml\n* Solução coroa: 3 seringas de 3ml\n* Solução xilo frente: 1 seringas de 3ml\n\nBLOQUEIO:\n* Bloqueio: Não\n* Seringas de bloqueio: \n* Comentários bloqueio: \n\nIMPLANTE SECUNDÁRIO: Não\n\n\nQUADRANTES (Área/Densidade/Furos/Fios):\n* Q1 (LE): 45cm² | 17.77777777777778 UF/cm² | 800 furos | 730 fios | Taxa quebra: 8.8%\n* Q2 (ME): 76cm² | 19.736842105263158 UF/cm² | 1500 furos | 1410 fios | Taxa quebra: 6.0%\n* Q3 (MD): 68cm² | 20.58823529411765 UF/cm² | 1400 furos | 1182 fios | Taxa quebra: 15.6%\n* Q4 (LD): 52cm² | 15.576923076923077 UF/cm² | 810 furos | 680 fios | Taxa quebra: 16.0%\n\n\nAVALIAÇÃO DA QUALIDADE (1=normal, 2=moderado, 3=intenso):\n* Infiltração: 1\n* Sedação: 1\n* Sangramento: 2\n\nMEDICAÇÕES UTILIZADAS:\n* Transamin: Não\n* Tadalafila: Não\n* Diprospam/Beta 30: Não\n\nHISTÓRICO MÉDICO:\n* Fumante: Não\n* Antecedente pessoal: Nega \n\n\n\nCOMENTÁRIOS GERAIS:\nFios de 2 e 3 médios e grossos		2026-03-10 18:05:05.03626	2026-03-10 18:05:05.03628	Capilar	scheduled	\N	\N
40	411	5	2026-03-04	* Data: 04/03/2026\n* Paciente: Rafael de Carvalho Nogueira \n* Unidade: Ribeirão Preto\n* Médico: Dr. Arthur\n* Equipe: Aline, Ana, Lavinia, Natália\n* Hora da cirurgia: 08:00\n* Tempo de cirurgia: 6h\n\nDADOS DA CIRURGIA:\n* Total de folículos: 4234\n\nÁREAS TRATADAS:\n* Frente: 3104\n* Coroa: 1130\n* Scalpe: \n* Península direita: 140\n* Península esquerda: 170\n\nRETOQUE: Não\nTIPO DE IMPLANTE: Exclusivo Capilar\n\n=== PROCEDIMENTOS E FERRAMENTAS ===\n* Safira: Não\n* Punch: 0,90x4mm\n\nSOLUÇÕES:\n* Solução frente: 4 seringas de 3ml\n* Solução coroa: 3 seringas de 3ml\n* Solução xilo frente: 1 seringas de 3ml\n\nBLOQUEIO:\n* Bloqueio: Não\n* Seringas de bloqueio: \n* Comentários bloqueio: \n\nIMPLANTE SECUNDÁRIO: Não\n\n\nQUADRANTES (Área/Densidade/Furos/Fios):\n* Q1 (LE): 49cm² | 16.3265306122449 UF/cm² | 800 furos | 737 fios | Taxa quebra: 7.9%\n* Q2 (ME): 95cm² | 15.789473684210526 UF/cm² | 1500 furos | 1436 fios | Taxa quebra: 4.3%\n* Q3 (MD): 90cm² | 18.333333333333332 UF/cm² | 1650 furos | 1440 fios | Taxa quebra: 12.7%\n* Q4 (LD): 56cm² | 11.607142857142858 UF/cm² | 650 furos | 621 fios | Taxa quebra: 4.5%\n\n\nAVALIAÇÃO DA QUALIDADE (1=normal, 2=moderado, 3=intenso):\n* Infiltração: 1\n* Sedação: 2\n* Sangramento: 2\n\nMEDICAÇÕES UTILIZADAS:\n* Transamin: Não\n* Tadalafila: Não\n* Diprospam/Beta 30: Não\n\nHISTÓRICO MÉDICO:\n* Fumante: Não\n* Antecedente pessoal: Nega\n\n\n\nCOMENTÁRIOS GERAIS:\nFeito Fentanil.\nFios de 1 e 2 espessura fina e comprimento médio.		2026-03-11 13:16:04.741265	2026-03-11 13:16:04.741304	Capilar	scheduled	\N	\N
41	413	5	2026-03-12	fazer frontal abaixando 1 dedo coroa e fazer denso\ntambem o resto patchwork	\N	2026-03-12 00:32:57.050357	2026-03-12 00:55:53.466271	transplante_capilar	scheduled	\N	\N
42	405	5	2026-03-05	* Data: 05/03/2026\n* Paciente: Vinicius Rocha Marques \n* Unidade: Ribeirão Preto\n* Médico: Dr. Arthur\n* Equipe: Aline, Ana, Lavinia, Natália\n* Hora da cirurgia: 08:00\n* Tempo de cirurgia: 5h\n\nDADOS DA CIRURGIA:\n* Total de folículos: 4524\n\nÁREAS TRATADAS:\n* Frente: 2245\n* Coroa: 1500\n* Scalpe: 779\n* Península direita: \n* Península esquerda: \n\nRETOQUE: Não\nTIPO DE IMPLANTE: Body Hair\n\n=== PROCEDIMENTOS E FERRAMENTAS ===\n* Safira: Não\n* Punch: 1,0x4mm\n\nSOLUÇÕES:\n* Solução frente: 4 seringas de 3ml\n* Solução coroa: 7 seringas de 3ml\n* Solução xilo frente: 1 seringas de 3ml\n\nBLOQUEIO:\n* Bloqueio: Não\n* Seringas de bloqueio: \n* Comentários bloqueio: \n\nIMPLANTE SECUNDÁRIO: Sim\n\n\nPELOS CORPORAIS:\n* Pelos corporais: Sim\n* Barba - Furos: 0 | Fios: 0 | Comentários: \n* Peitoral - Furos: 1530 | Fios: 1170 | Comentários: \n* Abdome - Furos: 1450 | Fios: 842 | Comentários: \n* Dorso - Furos:  | Fios:  | Comentários: \n* Pernas - Furos: 0 | Fios: 0 | Comentários: \n\nQUADRANTES (Área/Densidade/Furos/Fios):\n* Q1 (LE): 49cm² | 11.224489795918368 UF/cm² | 550 furos | 479 fios | Taxa quebra: 12.9%\n* Q2 (ME): 76cm² | 12.5 UF/cm² | 950 furos | 840 fios | Taxa quebra: 11.6%\n* Q3 (MD): 76cm² | 11.18421052631579 UF/cm² | 850 furos | 758 fios | Taxa quebra: 10.8%\n* Q4 (LD): 49cm² | 10.612244897959183 UF/cm² | 520 furos | 436 fios | Taxa quebra: 16.2%\n\n\nAVALIAÇÃO DA QUALIDADE (1=normal, 2=moderado, 3=intenso):\n* Infiltração: 3\n* Sedação: 2\n* Sangramento: 2\n\nMEDICAÇÕES UTILIZADAS:\n* Transamin: Não\n* Tadalafila: Não\n* Diprospam/Beta 30: Não\n\nHISTÓRICO MÉDICO:\n* Fumante: Não\n* Antecedente pessoal: Nao\n\n\n\nCOMENTÁRIOS GERAIS:\nFios de 1 e 2 fino e médio \n\nHAS		2026-03-12 13:44:32.291146	2026-03-12 13:44:32.291171	Body Hair	scheduled	\N	\N
\.


--
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public."user" (id, email, password_hash, name, role, specialty, created_at, username, role_clinico) FROM stdin;
11	admin@example.com	scrypt:32768:8:1$Uv5STmk8BzTnntlw$9bdc118fac9821ac4c09d14a8b44a13956443f862dcb7e651faae94ff051013baaac7ae3d729f1536a4b46aa113f0a78bb7dadb9d06c25ebeda6932bc3da5ad0	Admin	medico	\N	2026-03-03 19:27:03.03351	\N	DERM
9	clinicabasile@gmail.com	scrypt:32768:8:1$12hXSzYbSKBplxhI$cf7da4765c2cf74dbc18cecde1383d2f109a395d135820b3ab3ca35beabd59d3c72ce16edf36c9606620a705b9f42bc7e82cb3c852ba942149ce248b5dbc80be	Gisele	secretaria	\N	2026-01-21 14:49:13.980855	gisele	SECRETARY
10	erica.icb	scrypt:32768:8:1$bCSzsdYw0R4gzy9S$90b4c24c5241ddebc92f1f67f60b2b947259c4bbed377f9a16469382ab7af6c0d84eba40a8f2215875f17f8653b6c0fb736b7e29cf9365594d0cb249dae0ada9	Erica	secretaria	\N	2026-03-03 18:41:12.189318	erica	SECRETARY
7	filipe@clinicabasile.com	scrypt:32768:8:1$RceyXVu08E5FVamb$97e715a2cbb25891688f051498b0d2fe7d7f959f5783c84f502b5724eb502a748590c146d41a0000cd9e3ea07ffa5bcee09142e873f741773e315ea193e33124	Dr. Filipe	medico	dermatologista	2025-11-25 17:46:50.34006	fibasile	CP
6	vinicius@clinicabasile.com	scrypt:32768:8:1$fq50EHtKeH09Qmiw$b5e893c88e279b4943765e25dedd54aa1aeb67437def1435f0ed4a9185217b4a8d21060c39cc3067f87d07b861c25a1f5cff41d2c8f8841dbb8b1d8779089cf0	Dr. Vinicius	medico	dermatologista	2025-11-25 17:46:50.027331	vinibasile	CP
8	basile@clinicabasile.com	scrypt:32768:8:1$wJ7NdVjSxrKx1zVS$cbdb3583a5c73a39290ffc1d4346e25ffd82a6b830621edac25a751b3d90449693cf0f5c82ae87bfc63c2845d8dca31fed2a9f0ffc1af5a456fb775cd9768e4b	Dr. Basile	medico	dermatologista	2025-11-25 17:46:50.57519	rbasile	CP
12	Implantecapilaremrp@gmail.com	scrypt:32768:8:1$ed335lGYKzauDa2g$055f1d6d5acff5ea2d1a450a46ffbd9aedfa52eb0b8717a6f9bcc25ed3241427fc371c566a53e8ecd59261235d478c021ec9a685e8482cb37de5b55c3288175c	Erica	secretaria	\N	2026-03-03 19:46:20.419038	erica_old	SECRETARY
4	secretaria@clinicabasiledemo.com	scrypt:32768:8:1$2h5bpzRkmOu2RBOc$3d2913ea9e7906dcefd99cd6222416e44be9a2ff81ff508759192a7229a9ec442967f6e4e0b1b1089be9a8037a0a9637ca6ffa372182139012e97e6217717187	Secretária	secretaria	\N	2025-11-25 15:50:34.10396	Implantecapilaremrp@gmail.com	SECRETARY
5	arthur@clinicabasiledemo.com	scrypt:32768:8:1$vh6hzgJ5L4ueMjAU$c945196923c4a54c46f416fa67a6a65e9ab81a273686af6fcd7424c5c5d1112b7f52eff00819a55ea7684813d92fe0bf2185f19dde75ea7cc32f3577fa6880a6	Dr. Arthur	medico	dermatologista	2025-11-25 17:46:49.788963	tubasile	DERM
13	marcella@basile.com	scrypt:32768:8:1$F5EAGjDDuv7GOjky$b4cdf83bf056ade10f75af11cba59b5524adc8675c9a7fee1ab2d743f1ed511a51f1350bb573c57ebd0433c2943f2842847ceebdba5dfab4fa4fe0013bd8c57c	Marcella	secretaria	\N	2026-03-12 12:36:30.205487	marcella	SECRETARY
\.


--
-- Name: appointment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.appointment_id_seq', 492, true);


--
-- Name: attachment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.attachment_id_seq', 1, false);


--
-- Name: budget_cp_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.budget_cp_id_seq', 2, true);


--
-- Name: chat_message_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.chat_message_id_seq', 41, true);


--
-- Name: commercial_task_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.commercial_task_id_seq', 506, true);


--
-- Name: cosmetic_procedure_plan_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.cosmetic_procedure_plan_id_seq', 261, true);


--
-- Name: doctor_preference_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.doctor_preference_id_seq', 1, false);


--
-- Name: encounter_cp_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.encounter_cp_id_seq', 2, true);


--
-- Name: evolution_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.evolution_id_seq', 196, true);


--
-- Name: follow_up_reminder_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.follow_up_reminder_id_seq', 119, true);


--
-- Name: hair_transplant_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.hair_transplant_id_seq', 50, true);


--
-- Name: indication_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.indication_id_seq', 1, false);


--
-- Name: medication_usage_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.medication_usage_id_seq', 185, true);


--
-- Name: medications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.medications_id_seq', 344, true);


--
-- Name: message_read_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.message_read_id_seq', 39, true);


--
-- Name: note_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.note_id_seq', 583, true);


--
-- Name: operating_room_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.operating_room_id_seq', 1, true);


--
-- Name: patient_doctor_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.patient_doctor_id_seq', 422, true);


--
-- Name: patient_funnel_status_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.patient_funnel_status_id_seq', 1, true);


--
-- Name: patient_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.patient_id_seq', 420, true);


--
-- Name: patient_tag_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.patient_tag_id_seq', 1, false);


--
-- Name: payment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.payment_id_seq', 103, true);


--
-- Name: plan_cp_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.plan_cp_id_seq', 2, true);


--
-- Name: prescription_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.prescription_id_seq', 76, true);


--
-- Name: procedure_follow_up_rule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.procedure_follow_up_rule_id_seq', 1, false);


--
-- Name: procedure_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.procedure_id_seq', 5, true);


--
-- Name: procedure_record_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.procedure_record_id_seq', 1, false);


--
-- Name: surgery_evolution_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.surgery_evolution_id_seq', 34, true);


--
-- Name: surgery_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.surgery_id_seq', 19, true);


--
-- Name: tag_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.tag_id_seq', 1, false);


--
-- Name: transplant_image_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.transplant_image_id_seq', 1, false);


--
-- Name: transplant_surgery_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.transplant_surgery_id_seq', 1, false);


--
-- Name: transplant_surgery_record_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.transplant_surgery_record_id_seq', 42, true);


--
-- Name: user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.user_id_seq', 13, true);


--
-- Name: message_read _message_user_uc; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.message_read
    ADD CONSTRAINT _message_user_uc UNIQUE (message_id, user_id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: appointment appointment_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.appointment
    ADD CONSTRAINT appointment_pkey PRIMARY KEY (id);


--
-- Name: attachment attachment_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.attachment
    ADD CONSTRAINT attachment_pkey PRIMARY KEY (id);


--
-- Name: budget_cp budget_cp_encounter_id_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.budget_cp
    ADD CONSTRAINT budget_cp_encounter_id_key UNIQUE (encounter_id);


--
-- Name: budget_cp budget_cp_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.budget_cp
    ADD CONSTRAINT budget_cp_pkey PRIMARY KEY (id);


--
-- Name: chat_message chat_message_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.chat_message
    ADD CONSTRAINT chat_message_pkey PRIMARY KEY (id);


--
-- Name: commercial_task commercial_task_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.commercial_task
    ADD CONSTRAINT commercial_task_pkey PRIMARY KEY (id);


--
-- Name: cosmetic_procedure_plan cosmetic_procedure_plan_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.cosmetic_procedure_plan
    ADD CONSTRAINT cosmetic_procedure_plan_pkey PRIMARY KEY (id);


--
-- Name: doctor_preference doctor_preference_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.doctor_preference
    ADD CONSTRAINT doctor_preference_pkey PRIMARY KEY (id);


--
-- Name: doctor_preference doctor_preference_user_id_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.doctor_preference
    ADD CONSTRAINT doctor_preference_user_id_key UNIQUE (user_id);


--
-- Name: encounter_cp encounter_cp_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.encounter_cp
    ADD CONSTRAINT encounter_cp_pkey PRIMARY KEY (id);


--
-- Name: evolution evolution_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.evolution
    ADD CONSTRAINT evolution_pkey PRIMARY KEY (id);


--
-- Name: follow_up_reminder follow_up_reminder_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.follow_up_reminder
    ADD CONSTRAINT follow_up_reminder_pkey PRIMARY KEY (id);


--
-- Name: hair_transplant hair_transplant_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.hair_transplant
    ADD CONSTRAINT hair_transplant_pkey PRIMARY KEY (id);


--
-- Name: indication indication_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.indication
    ADD CONSTRAINT indication_pkey PRIMARY KEY (id);


--
-- Name: medication_usage medication_usage_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.medication_usage
    ADD CONSTRAINT medication_usage_pkey PRIMARY KEY (id);


--
-- Name: medications medications_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.medications
    ADD CONSTRAINT medications_pkey PRIMARY KEY (id);


--
-- Name: message_read message_read_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.message_read
    ADD CONSTRAINT message_read_pkey PRIMARY KEY (id);


--
-- Name: note note_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.note
    ADD CONSTRAINT note_pkey PRIMARY KEY (id);


--
-- Name: operating_room operating_room_name_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.operating_room
    ADD CONSTRAINT operating_room_name_key UNIQUE (name);


--
-- Name: operating_room operating_room_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.operating_room
    ADD CONSTRAINT operating_room_pkey PRIMARY KEY (id);


--
-- Name: patient_doctor patient_doctor_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.patient_doctor
    ADD CONSTRAINT patient_doctor_pkey PRIMARY KEY (id);


--
-- Name: patient_funnel_status patient_funnel_status_patient_id_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.patient_funnel_status
    ADD CONSTRAINT patient_funnel_status_patient_id_key UNIQUE (patient_id);


--
-- Name: patient_funnel_status patient_funnel_status_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.patient_funnel_status
    ADD CONSTRAINT patient_funnel_status_pkey PRIMARY KEY (id);


--
-- Name: patient patient_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.patient
    ADD CONSTRAINT patient_pkey PRIMARY KEY (id);


--
-- Name: patient_tag patient_tag_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.patient_tag
    ADD CONSTRAINT patient_tag_pkey PRIMARY KEY (id);


--
-- Name: payment payment_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.payment
    ADD CONSTRAINT payment_pkey PRIMARY KEY (id);


--
-- Name: plan_cp plan_cp_encounter_id_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.plan_cp
    ADD CONSTRAINT plan_cp_encounter_id_key UNIQUE (encounter_id);


--
-- Name: plan_cp plan_cp_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.plan_cp
    ADD CONSTRAINT plan_cp_pkey PRIMARY KEY (id);


--
-- Name: prescription prescription_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.prescription
    ADD CONSTRAINT prescription_pkey PRIMARY KEY (id);


--
-- Name: procedure_follow_up_rule procedure_follow_up_rule_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.procedure_follow_up_rule
    ADD CONSTRAINT procedure_follow_up_rule_pkey PRIMARY KEY (id);


--
-- Name: procedure_follow_up_rule procedure_follow_up_rule_procedure_name_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.procedure_follow_up_rule
    ADD CONSTRAINT procedure_follow_up_rule_procedure_name_key UNIQUE (procedure_name);


--
-- Name: procedure procedure_name_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.procedure
    ADD CONSTRAINT procedure_name_key UNIQUE (name);


--
-- Name: procedure procedure_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.procedure
    ADD CONSTRAINT procedure_pkey PRIMARY KEY (id);


--
-- Name: procedure_record procedure_record_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.procedure_record
    ADD CONSTRAINT procedure_record_pkey PRIMARY KEY (id);


--
-- Name: surgery_evolution surgery_evolution_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.surgery_evolution
    ADD CONSTRAINT surgery_evolution_pkey PRIMARY KEY (id);


--
-- Name: surgery surgery_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.surgery
    ADD CONSTRAINT surgery_pkey PRIMARY KEY (id);


--
-- Name: tag tag_name_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.tag
    ADD CONSTRAINT tag_name_key UNIQUE (name);


--
-- Name: tag tag_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.tag
    ADD CONSTRAINT tag_pkey PRIMARY KEY (id);


--
-- Name: transplant_image transplant_image_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.transplant_image
    ADD CONSTRAINT transplant_image_pkey PRIMARY KEY (id);


--
-- Name: transplant_surgery transplant_surgery_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.transplant_surgery
    ADD CONSTRAINT transplant_surgery_pkey PRIMARY KEY (id);


--
-- Name: transplant_surgery_record transplant_surgery_record_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.transplant_surgery_record
    ADD CONSTRAINT transplant_surgery_record_pkey PRIMARY KEY (id);


--
-- Name: patient_doctor unique_patient_doctor; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.patient_doctor
    ADD CONSTRAINT unique_patient_doctor UNIQUE (patient_id, doctor_id);


--
-- Name: commercial_task uq_commercial_task_consultation_source; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.commercial_task
    ADD CONSTRAINT uq_commercial_task_consultation_source UNIQUE (consultation_id, source_type);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: idx_appointment_doctor_date; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_appointment_doctor_date ON public.appointment USING btree (doctor_id, start_time);


--
-- Name: idx_appointment_start_time; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_appointment_start_time ON public.appointment USING btree (start_time);


--
-- Name: idx_cosmetic_procedure_plan_note; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_cosmetic_procedure_plan_note ON public.cosmetic_procedure_plan USING btree (note_id);


--
-- Name: idx_doctor_code; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_doctor_code ON public.patient_doctor USING btree (doctor_id, patient_code);


--
-- Name: idx_evolution_evolution_date; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_evolution_evolution_date ON public.evolution USING btree (evolution_date);


--
-- Name: idx_evolution_patient_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_evolution_patient_id ON public.evolution USING btree (patient_id);


--
-- Name: idx_follow_up_reminder_patient_procedure; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_follow_up_reminder_patient_procedure ON public.follow_up_reminder USING btree (patient_id, procedure_name);


--
-- Name: idx_follow_up_reminder_status; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_follow_up_reminder_status ON public.follow_up_reminder USING btree (status);


--
-- Name: idx_indication_note; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_indication_note ON public.indication USING btree (note_id);


--
-- Name: idx_message_user; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_message_user ON public.message_read USING btree (message_id, user_id);


--
-- Name: idx_note_patient_appt_type; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_note_patient_appt_type ON public.note USING btree (patient_id, appointment_id, note_type);


--
-- Name: idx_note_patient_category; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_note_patient_category ON public.note USING btree (patient_id, category);


--
-- Name: idx_procedure_followup; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_procedure_followup ON public.procedure_record USING btree (follow_up_due_at, follow_up_status);


--
-- Name: idx_procedure_patient_status; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_procedure_patient_status ON public.procedure_record USING btree (patient_id, status);


--
-- Name: idx_surgery_evolution_created_at; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_surgery_evolution_created_at ON public.surgery_evolution USING btree (created_at);


--
-- Name: idx_surgery_evolution_date; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_surgery_evolution_date ON public.surgery_evolution USING btree (evolution_date);


--
-- Name: idx_surgery_evolution_surgery_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_surgery_evolution_surgery_id ON public.surgery_evolution USING btree (surgery_id);


--
-- Name: idx_user_username; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX idx_user_username ON public."user" USING btree (username);


--
-- Name: ix_attachment_doctor_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_attachment_doctor_id ON public.attachment USING btree (doctor_id);


--
-- Name: ix_attachment_doctor_patient_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_attachment_doctor_patient_id ON public.attachment USING btree (doctor_patient_id);


--
-- Name: ix_commercial_task_consultation_date; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_commercial_task_consultation_date ON public.commercial_task USING btree (consultation_date);


--
-- Name: ix_commercial_task_consultation_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_commercial_task_consultation_id ON public.commercial_task USING btree (consultation_id);


--
-- Name: ix_commercial_task_created_at; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_commercial_task_created_at ON public.commercial_task USING btree (created_at);


--
-- Name: ix_commercial_task_doctor_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_commercial_task_doctor_id ON public.commercial_task USING btree (doctor_id);


--
-- Name: ix_commercial_task_next_followup_date; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_commercial_task_next_followup_date ON public.commercial_task USING btree (next_followup_date);


--
-- Name: ix_commercial_task_patient_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_commercial_task_patient_id ON public.commercial_task USING btree (patient_id);


--
-- Name: ix_commercial_task_source_type; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_commercial_task_source_type ON public.commercial_task USING btree (source_type);


--
-- Name: ix_commercial_task_status; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_commercial_task_status ON public.commercial_task USING btree (status);


--
-- Name: ix_encounter_cp_doctor_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_encounter_cp_doctor_id ON public.encounter_cp USING btree (doctor_id);


--
-- Name: ix_encounter_cp_doctor_patient_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_encounter_cp_doctor_patient_id ON public.encounter_cp USING btree (doctor_patient_id);


--
-- Name: ix_follow_up_reminder_scheduled_date; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_follow_up_reminder_scheduled_date ON public.follow_up_reminder USING btree (scheduled_date);


--
-- Name: ix_message_read_message_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_message_read_message_id ON public.message_read USING btree (message_id);


--
-- Name: ix_message_read_user_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_message_read_user_id ON public.message_read USING btree (user_id);


--
-- Name: ix_payment_appointment_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_payment_appointment_id ON public.payment USING btree (appointment_id);


--
-- Name: ix_payment_created_at; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_payment_created_at ON public.payment USING btree (created_at);


--
-- Name: ix_payment_patient_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_payment_patient_id ON public.payment USING btree (patient_id);


--
-- Name: ix_prescription_patient_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_prescription_patient_id ON public.prescription USING btree (patient_id);


--
-- Name: ix_procedure_record_follow_up_due_at; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_procedure_record_follow_up_due_at ON public.procedure_record USING btree (follow_up_due_at);


--
-- Name: ix_procedure_record_patient_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_procedure_record_patient_id ON public.procedure_record USING btree (patient_id);


--
-- Name: ix_procedure_record_performed_date; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_procedure_record_performed_date ON public.procedure_record USING btree (performed_date);


--
-- Name: ix_procedure_record_procedure_name; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_procedure_record_procedure_name ON public.procedure_record USING btree (procedure_name);


--
-- Name: ix_surgery_date; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_surgery_date ON public.surgery USING btree (date);


--
-- Name: ix_surgery_doctor_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_surgery_doctor_id ON public.surgery USING btree (doctor_id);


--
-- Name: ix_surgery_operating_room_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_surgery_operating_room_id ON public.surgery USING btree (operating_room_id);


--
-- Name: ix_surgery_start_time; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_surgery_start_time ON public.surgery USING btree (start_time);


--
-- Name: ix_transplant_surgery_record_doctor_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_transplant_surgery_record_doctor_id ON public.transplant_surgery_record USING btree (doctor_id);


--
-- Name: ix_transplant_surgery_record_patient_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_transplant_surgery_record_patient_id ON public.transplant_surgery_record USING btree (patient_id);


--
-- Name: ix_transplant_surgery_record_surgery_date; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_transplant_surgery_record_surgery_date ON public.transplant_surgery_record USING btree (surgery_date);


--
-- Name: ix_user_email; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX ix_user_email ON public."user" USING btree (email);


--
-- Name: appointment appointment_doctor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.appointment
    ADD CONSTRAINT appointment_doctor_id_fkey FOREIGN KEY (doctor_id) REFERENCES public."user"(id);


--
-- Name: appointment appointment_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.appointment
    ADD CONSTRAINT appointment_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: attachment attachment_doctor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.attachment
    ADD CONSTRAINT attachment_doctor_id_fkey FOREIGN KEY (doctor_id) REFERENCES public."user"(id);


--
-- Name: attachment attachment_doctor_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.attachment
    ADD CONSTRAINT attachment_doctor_patient_id_fkey FOREIGN KEY (doctor_patient_id) REFERENCES public.patient_doctor(id);


--
-- Name: budget_cp budget_cp_encounter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.budget_cp
    ADD CONSTRAINT budget_cp_encounter_id_fkey FOREIGN KEY (encounter_id) REFERENCES public.encounter_cp(id);


--
-- Name: chat_message chat_message_recipient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.chat_message
    ADD CONSTRAINT chat_message_recipient_id_fkey FOREIGN KEY (recipient_id) REFERENCES public."user"(id);


--
-- Name: chat_message chat_message_sender_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.chat_message
    ADD CONSTRAINT chat_message_sender_id_fkey FOREIGN KEY (sender_id) REFERENCES public."user"(id);


--
-- Name: commercial_task commercial_task_consultation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.commercial_task
    ADD CONSTRAINT commercial_task_consultation_id_fkey FOREIGN KEY (consultation_id) REFERENCES public.appointment(id);


--
-- Name: commercial_task commercial_task_doctor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.commercial_task
    ADD CONSTRAINT commercial_task_doctor_id_fkey FOREIGN KEY (doctor_id) REFERENCES public."user"(id);


--
-- Name: commercial_task commercial_task_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.commercial_task
    ADD CONSTRAINT commercial_task_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: cosmetic_procedure_plan cosmetic_procedure_plan_note_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.cosmetic_procedure_plan
    ADD CONSTRAINT cosmetic_procedure_plan_note_id_fkey FOREIGN KEY (note_id) REFERENCES public.note(id);


--
-- Name: doctor_preference doctor_preference_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.doctor_preference
    ADD CONSTRAINT doctor_preference_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: encounter_cp encounter_cp_doctor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.encounter_cp
    ADD CONSTRAINT encounter_cp_doctor_id_fkey FOREIGN KEY (doctor_id) REFERENCES public."user"(id);


--
-- Name: encounter_cp encounter_cp_doctor_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.encounter_cp
    ADD CONSTRAINT encounter_cp_doctor_patient_id_fkey FOREIGN KEY (doctor_patient_id) REFERENCES public.patient_doctor(id);


--
-- Name: evolution evolution_consultation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.evolution
    ADD CONSTRAINT evolution_consultation_id_fkey FOREIGN KEY (consultation_id) REFERENCES public.appointment(id);


--
-- Name: evolution evolution_doctor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.evolution
    ADD CONSTRAINT evolution_doctor_id_fkey FOREIGN KEY (doctor_id) REFERENCES public."user"(id);


--
-- Name: evolution evolution_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.evolution
    ADD CONSTRAINT evolution_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: follow_up_reminder follow_up_reminder_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.follow_up_reminder
    ADD CONSTRAINT follow_up_reminder_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: hair_transplant hair_transplant_note_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.hair_transplant
    ADD CONSTRAINT hair_transplant_note_id_fkey FOREIGN KEY (note_id) REFERENCES public.note(id);


--
-- Name: indication indication_note_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.indication
    ADD CONSTRAINT indication_note_id_fkey FOREIGN KEY (note_id) REFERENCES public.note(id);


--
-- Name: indication indication_procedure_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.indication
    ADD CONSTRAINT indication_procedure_id_fkey FOREIGN KEY (procedure_id) REFERENCES public.procedure(id);


--
-- Name: medication_usage medication_usage_medication_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.medication_usage
    ADD CONSTRAINT medication_usage_medication_id_fkey FOREIGN KEY (medication_id) REFERENCES public.medications(id);


--
-- Name: message_read message_read_message_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.message_read
    ADD CONSTRAINT message_read_message_id_fkey FOREIGN KEY (message_id) REFERENCES public.chat_message(id) ON DELETE CASCADE;


--
-- Name: message_read message_read_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.message_read
    ADD CONSTRAINT message_read_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id) ON DELETE CASCADE;


--
-- Name: note note_appointment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.note
    ADD CONSTRAINT note_appointment_id_fkey FOREIGN KEY (appointment_id) REFERENCES public.appointment(id);


--
-- Name: note note_doctor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.note
    ADD CONSTRAINT note_doctor_id_fkey FOREIGN KEY (doctor_id) REFERENCES public."user"(id);


--
-- Name: note note_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.note
    ADD CONSTRAINT note_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: patient_doctor patient_doctor_doctor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.patient_doctor
    ADD CONSTRAINT patient_doctor_doctor_id_fkey FOREIGN KEY (doctor_id) REFERENCES public."user"(id);


--
-- Name: patient_doctor patient_doctor_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.patient_doctor
    ADD CONSTRAINT patient_doctor_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: patient_funnel_status patient_funnel_status_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.patient_funnel_status
    ADD CONSTRAINT patient_funnel_status_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: patient_tag patient_tag_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.patient_tag
    ADD CONSTRAINT patient_tag_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: patient_tag patient_tag_tag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.patient_tag
    ADD CONSTRAINT patient_tag_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES public.tag(id);


--
-- Name: payment payment_appointment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.payment
    ADD CONSTRAINT payment_appointment_id_fkey FOREIGN KEY (appointment_id) REFERENCES public.appointment(id);


--
-- Name: payment payment_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.payment
    ADD CONSTRAINT payment_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: plan_cp plan_cp_encounter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.plan_cp
    ADD CONSTRAINT plan_cp_encounter_id_fkey FOREIGN KEY (encounter_id) REFERENCES public.encounter_cp(id);


--
-- Name: prescription prescription_appointment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.prescription
    ADD CONSTRAINT prescription_appointment_id_fkey FOREIGN KEY (appointment_id) REFERENCES public.appointment(id);


--
-- Name: prescription prescription_doctor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.prescription
    ADD CONSTRAINT prescription_doctor_id_fkey FOREIGN KEY (doctor_id) REFERENCES public."user"(id);


--
-- Name: prescription prescription_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.prescription
    ADD CONSTRAINT prescription_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: procedure_record procedure_record_doctor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.procedure_record
    ADD CONSTRAINT procedure_record_doctor_id_fkey FOREIGN KEY (doctor_id) REFERENCES public."user"(id);


--
-- Name: procedure_record procedure_record_evolution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.procedure_record
    ADD CONSTRAINT procedure_record_evolution_id_fkey FOREIGN KEY (evolution_id) REFERENCES public.evolution(id);


--
-- Name: procedure_record procedure_record_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.procedure_record
    ADD CONSTRAINT procedure_record_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: surgery surgery_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.surgery
    ADD CONSTRAINT surgery_created_by_fkey FOREIGN KEY (created_by) REFERENCES public."user"(id);


--
-- Name: surgery surgery_doctor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.surgery
    ADD CONSTRAINT surgery_doctor_id_fkey FOREIGN KEY (doctor_id) REFERENCES public."user"(id);


--
-- Name: surgery_evolution surgery_evolution_doctor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.surgery_evolution
    ADD CONSTRAINT surgery_evolution_doctor_id_fkey FOREIGN KEY (doctor_id) REFERENCES public."user"(id);


--
-- Name: surgery_evolution surgery_evolution_surgery_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.surgery_evolution
    ADD CONSTRAINT surgery_evolution_surgery_id_fkey FOREIGN KEY (surgery_id) REFERENCES public.transplant_surgery_record(id) ON DELETE CASCADE;


--
-- Name: surgery surgery_operating_room_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.surgery
    ADD CONSTRAINT surgery_operating_room_id_fkey FOREIGN KEY (operating_room_id) REFERENCES public.operating_room(id);


--
-- Name: surgery surgery_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.surgery
    ADD CONSTRAINT surgery_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: surgery surgery_procedure_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.surgery
    ADD CONSTRAINT surgery_procedure_id_fkey FOREIGN KEY (procedure_id) REFERENCES public.procedure(id);


--
-- Name: surgery surgery_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.surgery
    ADD CONSTRAINT surgery_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public."user"(id);


--
-- Name: transplant_image transplant_image_hair_transplant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.transplant_image
    ADD CONSTRAINT transplant_image_hair_transplant_id_fkey FOREIGN KEY (hair_transplant_id) REFERENCES public.hair_transplant(id);


--
-- Name: transplant_surgery transplant_surgery_hair_transplant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.transplant_surgery
    ADD CONSTRAINT transplant_surgery_hair_transplant_id_fkey FOREIGN KEY (hair_transplant_id) REFERENCES public.hair_transplant(id);


--
-- Name: transplant_surgery_record transplant_surgery_record_doctor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.transplant_surgery_record
    ADD CONSTRAINT transplant_surgery_record_doctor_id_fkey FOREIGN KEY (doctor_id) REFERENCES public."user"(id);


--
-- Name: transplant_surgery_record transplant_surgery_record_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.transplant_surgery_record
    ADD CONSTRAINT transplant_surgery_record_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: cloud_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE cloud_admin IN SCHEMA public GRANT ALL ON SEQUENCES TO neon_superuser WITH GRANT OPTION;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: cloud_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE cloud_admin IN SCHEMA public GRANT ALL ON TABLES TO neon_superuser WITH GRANT OPTION;


--
-- PostgreSQL database dump complete
--

\unrestrict Xj4s22dthD4q82U4uXoVRVQXElYpkrfRWnLOfFxyU1bJYCw7ObHM2okRHZ2q12V


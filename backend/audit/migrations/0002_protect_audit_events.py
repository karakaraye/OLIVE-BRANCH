from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("audit", "0001_initial")]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE FUNCTION audit_reject_event_changes() RETURNS trigger
                LANGUAGE plpgsql AS $$
                BEGIN
                    RAISE EXCEPTION 'Audit events are append-only' USING ERRCODE = '23000';
                END;
                $$;

                CREATE TRIGGER audit_event_append_only
                    BEFORE UPDATE OR DELETE ON audit_auditevent
                    FOR EACH ROW EXECUTE FUNCTION audit_reject_event_changes();

                CREATE TRIGGER audit_event_no_truncate
                    BEFORE TRUNCATE ON audit_auditevent
                    FOR EACH STATEMENT EXECUTE FUNCTION audit_reject_event_changes();
            """,
            reverse_sql="""
                DROP TRIGGER audit_event_no_truncate ON audit_auditevent;
                DROP TRIGGER audit_event_append_only ON audit_auditevent;
                DROP FUNCTION audit_reject_event_changes();
            """,
        ),
    ]

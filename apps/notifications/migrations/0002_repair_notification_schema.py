from django.db import migrations


def repair_notification_table(apps, schema_editor):
    table_name = "notifications_notification"
    connection = schema_editor.connection
    cursor = connection.cursor()
    columns = {
        column.name
        for column in connection.introspection.get_table_description(
            cursor,
            table_name,
        )
    }
    quoted_table = schema_editor.quote_name(table_name)

    missing_columns = {
        "text": "varchar(255) NOT NULL DEFAULT ''",
        "chat_message_id": "bigint NULL REFERENCES chat_message(id)",
        "sender_id": "bigint NOT NULL REFERENCES accounts_user(id)",
    }

    for column_name, definition in missing_columns.items():
        if column_name not in columns:
            schema_editor.execute(
                "ALTER TABLE %s ADD COLUMN %s %s"
                % (
                    quoted_table,
                    schema_editor.quote_name(column_name),
                    definition,
                )
            )


def reverse_repair_notification_table(apps, schema_editor):
    return None


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            repair_notification_table,
            reverse_code=reverse_repair_notification_table,
        ),
    ]

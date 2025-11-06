# main/migrations/0009_create_savedevent_if_missing.py
from django.db import migrations

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS `main_savedevent` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `event_id` BIGINT NOT NULL,
  `remind_me` BOOL NOT NULL DEFAULT 0,
  `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (`id`),
  UNIQUE KEY `main_savedevent_user_event_uniq` (`user_id`, `event_id`),
  KEY `main_savedevent_user_fk` (`user_id`),
  KEY `main_savedevent_event_fk` (`event_id`),
  CONSTRAINT `main_savedevent_user_fk`
    FOREIGN KEY (`user_id`) REFERENCES `main_user` (`user_id`)
    ON DELETE CASCADE,
  CONSTRAINT `main_savedevent_event_fk`
    FOREIGN KEY (`event_id`) REFERENCES `main_event` (`id`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

DROP_SQL = """
DROP TABLE IF EXISTS `main_savedevent`;
"""

class Migration(migrations.Migration):
    dependencies = [
        ("main", "0008_create_payment"),  # keep as-is
    ]
    operations = [
        migrations.RunSQL(sql=CREATE_SQL, reverse_sql=DROP_SQL),

from django.db import migrations

class Migration(migrations.Migration):
    # Keep the sequence intact, but do nothing here because
    # SavedEvent is already created in 0001_initial.
    dependencies = [
        ("main", "0008_create_payment"),
    ]

    operations = [
        # no-op on purpose
    ]

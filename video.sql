CREATE TABLE VIDEO (
id SERIAL PRIMARY KEY,
url VARCHAR(255),
embed_url VARCHAR(255),
video_id VARCHAR(255),
name VARCHAR(255),
description VARCHAR(255),
thumbnail_url VARCHAR(255),
channel VARCHAR(255),
date_published TIMESTAMP,
genre VARCHAR(255)
);

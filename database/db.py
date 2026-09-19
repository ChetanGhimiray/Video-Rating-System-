CREATE DATABASE video_grading_system;

USE video_grading_system;


-- =========================================
-- 1. VIDEO SUBMISSIONS
-- =========================================

CREATE TABLE video_submissions (
    video_id INT AUTO_INCREMENT PRIMARY KEY,
    video_name VARCHAR(255) NOT NULL,
    video_path VARCHAR(500),
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    duration_seconds DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'Pending'
);


-- =========================================
-- 2. SPEAKERS
-- =========================================

CREATE TABLE speakers (
    speaker_id INT AUTO_INCREMENT PRIMARY KEY,
    video_id INT NOT NULL,
    speaker_name VARCHAR(150),
    speaker_label VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (video_id)
        REFERENCES video_submissions(video_id)
        ON DELETE CASCADE
);


-- =========================================
-- 3. ASSESSMENT RESULTS
-- =========================================

CREATE TABLE assessment_results (
    assessment_id INT AUTO_INCREMENT PRIMARY KEY,
    video_id INT NOT NULL,
    speaker_id INT,

    fluency_score DECIMAL(5,2),
    eye_contact_score DECIMAL(5,2),
    pronunciation_score DECIMAL(5,2),
    confidence_score DECIMAL(5,2),

    assessment_time DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (video_id)
        REFERENCES video_submissions(video_id)
        ON DELETE CASCADE,

    FOREIGN KEY (speaker_id)
        REFERENCES speakers(speaker_id)
        ON DELETE SET NULL
);


-- =========================================
-- 4. FINAL RESULTS
-- =========================================

CREATE TABLE final_results (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    video_id INT NOT NULL,

    overall_score DECIMAL(5,2),
    grade VARCHAR(10),
    performance_level VARCHAR(50),
    feedback TEXT,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (video_id)
        REFERENCES video_submissions(video_id)
        ON DELETE CASCADE
);

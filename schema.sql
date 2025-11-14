-- Create database with proper charset for Nairobi location names
CREATE DATABASE IF NOT EXISTS `Aggregator` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE `Aggregator`;

-- Enable foreign key constraints
SET FOREIGN_KEY_CHECKS = 1;

-- Users table with enhanced security
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `email` VARCHAR(255) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `email_verified` BOOLEAN DEFAULT FALSE,
    `login_attempts` INT DEFAULT 0,
    `locked_until` DATETIME NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_user_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Properties table with Nairobi-specific locations
CREATE TABLE IF NOT EXISTS `properties` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `user_id` INT NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `type` ENUM(
        'Serviced Apartment', 'Boutique Hotel', 'Guest House', 'Luxury Villa',
        'Bed & Breakfast', 'Hostel', 'Lodge', 'Resort'
    ) NOT NULL DEFAULT 'Serviced Apartment',
    `location` ENUM(
        'Westlands', 'CBD', 'Kilimani', 'Karen', 'Lavington', 'Kileleshwa',
        'Parklands', 'Upper Hill', 'South B', 'South C', 'Ngong Road', 'Thika Road'
    ) NOT NULL DEFAULT 'Westlands',
    `base_price` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    `currency` VARCHAR(3) DEFAULT 'KES',
    `bedrooms` INT DEFAULT 1,
    `capacity` INT DEFAULT 2,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_property_user_location` (`user_id`, `location`),
    INDEX `idx_property_type_location` (`type`, `location`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Competitor prices with Nairobi market data
CREATE TABLE IF NOT EXISTS `competitor_prices` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `user_id` INT NOT NULL,
    `property_id` INT NOT NULL,
    `competitor_name` VARCHAR(255) NOT NULL,
    `platform` ENUM('Airbnb', 'Booking.com', 'Agoda', 'Expedia', 'Hotels.com', 'Direct Website') NOT NULL,
    `price` DECIMAL(10,2) NOT NULL,
    `currency` VARCHAR(3) DEFAULT 'KES',
    `date` DATE NOT NULL,
    `availability` ENUM('Available', 'Limited', 'Last Unit', 'Sold Out', 'Good Availability') DEFAULT 'Available',
    `min_stay` INT DEFAULT 1,
    `rating` DECIMAL(3,2) NULL,
    `review_count` INT DEFAULT 0,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`property_id`) REFERENCES `properties`(`id`) ON DELETE CASCADE,
    INDEX `idx_competitor_user_date` (`user_id`, `date`),
    INDEX `idx_competitor_property_date` (`property_id`, `date`),
    INDEX `idx_competitor_platform` (`platform`, `date`),
    UNIQUE KEY `unique_competitor_entry` (`user_id`, `property_id`, `competitor_name`, `date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Price forecasts table
CREATE TABLE IF NOT EXISTS `forecasts` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `user_id` INT NOT NULL,
    `property_id` INT NOT NULL,
    `date` DATE NOT NULL,
    `predicted_price` DECIMAL(10,2) NOT NULL,
    `confidence_interval` DECIMAL(5,2) DEFAULT 0.80,
    `model_info` VARCHAR(255),
    `seasonality_factor` DECIMAL(5,2) DEFAULT 1.0,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`property_id`) REFERENCES `properties`(`id`) ON DELETE CASCADE,
    INDEX `idx_forecast_user_property` (`user_id`, `property_id`),
    INDEX `idx_forecast_date` (`date`),
    UNIQUE KEY `unique_forecast_entry` (`user_id`, `property_id`, `date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
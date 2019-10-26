SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT = @@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS = @@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION = @@COLLATION_CONNECTION */;

CREATE USER 'matcha'@'%' IDENTIFIED WITH mysql_native_password BY 'absolutelySecret';
GRANT ALL ON *.* TO 'matcha'@'%';

--
-- База данных: `matcha`
--
CREATE DATABASE IF NOT EXISTS `matcha` DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;
USE `matcha`;

-- --------------------------------------------------------

--
-- Структура таблицы `users`
--

CREATE TABLE IF NOT EXISTS `users`
(
    `id`          int(11)                                                 NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `login`       varchar(20) COLLATE utf8_unicode_ci                     NOT NULL UNIQUE,
    `name`        varchar(20) COLLATE utf8_unicode_ci                     NOT NULL,
    `surname`     varchar(20) COLLATE utf8_unicode_ci                     NOT NULL UNIQUE,
    `email`       varchar(30) COLLATE utf8_unicode_ci                     NOT NULL,
    `password`    varchar(255) COLLATE utf8_unicode_ci                    NOT NULL,
    `token`       varchar(20) COLLATE utf8_unicode_ci                     NOT NULL,
    `confirmed`   tinyint(1)                                              NOT NULL                         DEFAULT '0',
    `gender`      enum ('male','female') CHARACTER SET utf8 COLLATE utf8_unicode_ci                        DEFAULT NULL,
    `preferences` enum ('bisexual','heterosexual','homosexual') CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
    `biography`   text COLLATE utf8_unicode_ci,
    `avatar`      varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci                                  DEFAULT NULL,
    `photos`      varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL                         DEFAULT '["", "", "", ""]',
    `age`         int(11)                                                                                  DEFAULT NULL,
    `online`      tinyint(1)                                              NOT NULL                         DEFAULT '0',
    `last_login`  datetime                                                                                 DEFAULT NULL,
    `city`        varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci                                  DEFAULT NULL
) ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `blocked`
--

CREATE TABLE IF NOT EXISTS `blocked`
(
    `id`         int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `user_id`    int(11) NOT NULL,
    `blocked_id` int(11) NOT NULL,
    CONSTRAINT fk_blocked_user_ref1 FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_blocked_user_ref2 FOREIGN KEY (blocked_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `likes`
--

CREATE TABLE IF NOT EXISTS `likes`
(
    `id`       int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY AUTO_INCREMENT,
    `user_id`  int(11) NOT NULL,
    `liked_id` int(11) NOT NULL,
    CONSTRAINT fk_likes_user_ref1 FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_likes_user_ref2 FOREIGN KEY (liked_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_unicode_ci;


-- --------------------------------------------------------

--
-- Структура таблицы `reports`
--

CREATE TABLE IF NOT EXISTS `reports`
(
    `id`          int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `user_id`     int(11) NOT NULL,
    `reported_id` int(11) NOT NULL,
    CONSTRAINT fk_reported_user_ref1 FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_reported_user_ref2 FOREIGN KEY (reported_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_unicode_ci;


-- --------------------------------------------------------

--
-- Структура таблицы `visits`
--

CREATE TABLE IF NOT EXISTS `visits`
(
    `id`         int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `user_id`    int(11) NOT NULL,
    `visited_id` int(11) NOT NULL,
    CONSTRAINT fk_visits_user_ref1 FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_visits_user_ref2 FOREIGN KEY (visited_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `chats`
--

CREATE TABLE `chats`
(
    `id`       int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `user1_id` int(11) NOT NULL,
    `user2_id` int(11) NOT NULL,
    CONSTRAINT fk_chats_user_ref1 FOREIGN KEY (user1_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_chats_user_ref2 FOREIGN KEY (user2_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `messages`
--

CREATE TABLE `messages`
(
    `id`           int(11)                                         NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `chat_id`      int(11)                                         NOT NULL,
    `sender_id`    int(11)                                         NOT NULL,
    `recipient_id` int(11)                                         NOT NULL,
    `text`         text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
    `timestamp`    datetime                                        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_messages_user_ref1 FOREIGN KEY (sender_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_messages_user_ref2 FOREIGN KEY (recipient_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT ft_messages_chat_ref FOREIGN KEY (chat_id) REFERENCES chats (id) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `notifications`
--

CREATE TABLE IF NOT EXISTS `notifications`
(
    `id`           int(11)                                                 NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `user_id`      int(11)                                                 NOT NULL,
    `message`      text CHARACTER SET utf8 COLLATE utf8_unicode_ci         NOT NULL,
    `link`         varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
    `date_created` datetime                                                NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_notifications_user_ref FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `tags`
--

CREATE TABLE IF NOT EXISTS `tags`
(
    `id`   int(11)                             NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` varchar(20) COLLATE utf8_unicode_ci NOT NULL UNIQUE
) ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `user_tag`
--

CREATE TABLE IF NOT EXISTS `user_tag`
(
    `id`      int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `user_id` int(11) NOT NULL,
    `tag_id`  int(11) NOT NULL,
    CONSTRAINT fk_user_tag_user_ref FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_user_tag_tag_ref FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_unicode_ci;

/*!40101 SET CHARACTER_SET_CLIENT = @OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS = @OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION = @OLD_COLLATION_CONNECTION */;

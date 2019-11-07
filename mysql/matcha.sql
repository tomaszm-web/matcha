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

INSERT INTO matcha.users (id, login, name, surname, email, password, token, confirmed, gender, preferences, biography, avatar, photos, age, online, last_login, city) VALUES (1, 'o4eredko', 'Yevhenii', 'Ocheredko', 'evgeny.ocheredko@gmail.com', 'pbkdf2:sha256:150000$xkIs6yQW$a2e4aa7c385f9b21b3a69260d70a4e231f1b0bf16ba4ca23e9d5a440249ff9fa', 'cfb30c8ff2224ee79f7b', 1, 'male', 'heterosexual', 'Hello world!', '/uploads/o4eredko/large_yochered.jpg', '["", "", "", ""]', 18, 0, '2019-11-07 10:56:55', 'Kyiv, Ukraine');
INSERT INTO matcha.users (id, login, name, surname, email, password, token, confirmed, gender, preferences, biography, avatar, photos, age, online, last_login, city) VALUES (2, 'anfisa_lm', 'Anfisa', 'Laminatuer', 'anfisa228@matcha.com', 'pbkdf2:sha256:150000$57Zgbx71$a143f74db5a603f891a24da496d61b1cace154fceb1c5e5099ca8d3efa20b8f7', 'b87a1a8e514c6f721357', 1, 'female', 'bisexual', 'Sympotichaya devochka', '/uploads/anfisa_lm/000036.jpg', '["", "", "", ""]', 19, 0, '2019-11-07 10:27:42', 'Kyiv, Ukraine');
INSERT INTO matcha.users (id, login, name, surname, email, password, token, confirmed, gender, preferences, biography, avatar, photos, age, online, last_login, city) VALUES (3, 'f_drakul', 'Fleur', 'DeLacoure', 'f.drakul@matcha.com', 'pbkdf2:sha256:150000$mpUd83es$e1b108f7864a386c50a90da9fa0d40914b04cf7ae764799bb77eb737c7a25152', 'df011f8cb36e5eb9734e', 1, 'female', 'heterosexual', 'Blogger', '/uploads/f_drakul/000049.jpg', '["", "", "", ""]', 25, 0, '2019-11-07 10:25:15', 'Kyiv, Ukraine');
INSERT INTO matcha.users (id, login, name, surname, email, password, token, confirmed, gender, preferences, biography, avatar, photos, age, online, last_login, city) VALUES (4, 'koval', 'Will', 'Terner', 'koval@matcha.com', 'pbkdf2:sha256:150000$rVMadgI5$27e405e4fb04ae2630bba89ae92bb0d5423dab2fc31e097ac437ccbdc17d9f9f', 'ab8e8fe2ab622f9eb463', 1, null, null, null, null, '["", "", "", ""]', null, 0, null, null);
INSERT INTO matcha.users (id, login, name, surname, email, password, token, confirmed, gender, preferences, biography, avatar, photos, age, online, last_login, city) VALUES (5, 'glad', 'Glad', 'Valakas', 'glad.valakas@matcha.com', 'pbkdf2:sha256:150000$3fKsKjjB$8e2cfa6c9c6e41410f4a951fe1ffd3feb127ef73a1868cb5cbd2b716fa5a6385', 'bf7aeb06763b1fa17bc4', 1, 'male', 'heterosexual', 'Blogger, Billionaire', '/uploads/glad/glad.jpg', '["", "", "", ""]', 64, 0, '2019-11-07 10:24:29', 'Zhytomyr, Zhytomyr Oblast, Ukraine');
INSERT INTO matcha.users (id, login, name, surname, email, password, token, confirmed, gender, preferences, biography, avatar, photos, age, online, last_login, city) VALUES (6, 'laroft', 'Larisa', 'Croft', 'laracroft@matcha.com', 'pbkdf2:sha256:150000$wzDnincT$8bd8993a79bc9720e90199678b75d872c4fe4ceff64359c7b046d84d41f3531f', '3af164da7c5e5fcca6ee', 1, 'female', 'heterosexual', 'I am not Russia', '/uploads/laroft/girl1.jpg', '["", "", "", ""]', 21, 0, '2019-11-07 10:28:39', 'Kyiv, Ukraine');
INSERT INTO matcha.users (id, login, name, surname, email, password, token, confirmed, gender, preferences, biography, avatar, photos, age, online, last_login, city) VALUES (7, 'login', 'Login', 'Passwordovich', 'login@matcha.com', 'pbkdf2:sha256:150000$KgUu1ORV$14339be8b0429440ae4cd567f6301850fb10c0fad65eea91af8f7d5231c116e2', '8897dec0ac7b5f805e95', 1, 'female', 'bisexual', 'I''m the beta-tester of this damn site. My avatar is AI generated face.', '/uploads/login/000041.jpg', '["", "", "", ""]', 23, 0, '2019-11-07 11:04:07', 'Brussels, Belgium');
INSERT INTO matcha.users (id, login, name, surname, email, password, token, confirmed, gender, preferences, biography, avatar, photos, age, online, last_login, city) VALUES (8, 'aspizhav', 'Andy', 'Spizhavka', 'aspizhav@matcha.com', 'pbkdf2:sha256:150000$1QwsY9Fd$e6e589a9fcb7da46badb8673aaac75dfb8c2aa5ce1c0f86801167b95beaf2efd', '0a8f48791d08a64b5667', 1, 'male', 'heterosexual', 'Sportsmen, programmer, handsome, liar', '/uploads/aspizhav/man1.jpg', '["", "", "", ""]', 19, 0, '2019-11-07 10:29:25', 'Chernivtsi, Chernivtsi Oblast, Ukraine');

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

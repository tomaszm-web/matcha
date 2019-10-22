SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT = @@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS = @@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION = @@COLLATION_CONNECTION */;

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

--
-- Дамп данных таблицы `users`
--

INSERT INTO `users` (`id`, `login`, `name`, `surname`, `email`, `password`, `token`, `confirmed`, `gender`,
                     `preferences`, `biography`, `avatar`, `photos`, `age`, `online`, `last_login`, `city`)
VALUES (44, 'login', 'Mykola', 'Kostiantynovich', 'o4eredko.crypto@gmail.com',
        'pbkdf2:sha256:150000$zXhR3POx$aac96921bede1fc55dd8c3e1680541695436b1243cc463054f2d36dbdf729cfc',
        'c2dfc6a5e44f3c0c8518', 1, 'female', 'bisexual', 'Are you Okay?', '/uploads/avatar.png',
        '[\"/uploads/afrodita/obama3.jpeg\", \"\", \"\", \"\"]', 18, 0, '2019-10-08 14:27:21', NULL),
       (46, 'afrodita', 'Afrodita', 'Kardashian', 'suyuvumiwu@quickemail.info',
        'pbkdf2:sha256:150000$2XeI1DDS$2757329318b832f743ba7451860425f0428472515926b423dfd96cce97006fbf',
        'cefab73d61bb09d9b032', 1, 'female', 'heterosexual', 'Afganistan one love', '/uploads/avatar.png',
        '[\"/uploads/afrodita/obama3.jpeg\", \"\", \"uploads/afrodita/IMG_20170520_213128_785.jpg\", \"\"]', 21, 1,
        '2019-10-18 17:13:49', 'Kyiv, Ukraine'),
       (47, 'azbek', 'Azbek', 'Farhad', 'getamazid@tempmailapp.com',
        'pbkdf2:sha256:150000$9YkQ0zLb$f6662b9d4772c0150b87d1dfd5b322873b17f89ae70c59f2713676abe09dcff9',
        '03ac105048c7a1d87b8f', 1, 'male', 'heterosexual', 'Allah nad nami, Zemlya pod nogami', '/uploads/avatar.png',
        '[\"/uploads/afrodita/obama3.jpeg\", \"\", \"\", \"\"]', 35, 0, NULL, NULL),
       (48, 'okherson', 'Oleksii', 'Khersoniuk', 'wufigiluse@4easyemail.com',
        'pbkdf2:sha256:150000$bFKBmSHI$2a57db4514c5bfdcc821a47081f8d9dbf86dd8e6eb656d1226b4533473d92e6e',
        '7c4bb8564698e8bbed39', 1, 'male', 'heterosexual', NULL, '/uploads/avatar.png',
        '[\"/uploads/afrodita/obama3.jpeg\", \"\", \"\", \"\"]', 28, 0, NULL, NULL),
       (50, 'lara', 'Larisa', 'Pindoska', 'vefatufapo@mail-point.net',
        'pbkdf2:sha256:150000$wa1xr3EN$b45d57bb8983476a4a57e58db48c11a93bc686121c8213af45f23cbb753775ec',
        '1517e11c2286661f52d7', 1, 'female', 'heterosexual', 'Drunk as fucked', '/uploads/avatar.png',
        '[\"/uploads/afrodita/obama3.jpeg\", \"\", \"\", \"\"]', 18, 0, '2019-10-19 21:34:00', 'Kyiv, Ukraine'),
       (59, 'maximilian', 'Maximilian', 'Moskaloder', 'wilep@inappmail.com',
        'pbkdf2:sha256:150000$HjJUYSbZ$b56c68724963989061260fcfe11a76da7be93d148901a4e63ff0d3a8bd3c9c36',
        'e0545d6a928ee28dd151', 1, 'male', 'bisexual', 'Hello world', '/uploads/maximilian/large_yochered.jpg',
        '[\"/uploads/maximilian/large_yochered.jpg\", \"\", \"uploads/maximilian/large_yochered.jpg\", \"\"]', 20, 0,
        '2019-10-19 16:36:34', 'Kherson, Kherson Oblast, Ukraine'),
       (60, 'fdsafdas', 'Kostik', 'AAA', 'jecaxarih@my6mail.com',
        'pbkdf2:sha256:150000$qptlztYP$c744f940f3f478a156b28ef559b646ced9dbd6715878b7fd89d6cef053426df8',
        'd49e5fd8d4d9345ac029', 1, 'male', 'bisexual', 'AAAA', '/uploads/avatar.png', '[\"\", \"\", \"\", \"\"]', 21, 0,
        '2019-10-06 10:28:30', NULL),
       (61, 'dzaporoz2', 'Dmytro', 'Zzzz', 'bixap@my6mail.com',
        'pbkdf2:sha256:150000$Yj8mqV1b$c3b1c8a1cff69c2abb1be820a551c9b9a9ee08e8b6ff457236d46727d7493450',
        '6dafb79f682347a15587', 1, 'male', 'bisexual', 'biography', '/uploads/avatar.png',
        '[\"/uploads/dzaporoz2/1565540964.png\", \"/uploads/dzaporoz2/3.jpg\", \"\", \"\"]', 64, 0,
        '2019-10-06 13:07:35', 'Kyiv, Ukraine'),
       (62, 'mykola', 'Mykolai', 'Saint', 'ripanoxey@app-mailer.com',
        'pbkdf2:sha256:150000$VD3ld1zu$f06834980fe49046f5d5b591f384de3dc061a1f8a4bf87696e901116a7a9cffe',
        '14c1fb0a66cb9f59a788', 1, NULL, 'bisexual', NULL, '/static/img/default_avatar.png', '[\"\", \"\", \"\", \"\"]',
        18, 0, '2019-10-06 13:08:22', NULL),
       (63, 'o4eredko', 'Yevhenii', 'Ocheredko', 'evgeny.ocheredko@gmail.com',
        'pbkdf2:sha256:150000$aPuxewzR$8402898026f683a27addc11db980db544c16161b188f59a739d26dbce1da6129',
        'd19e412b481599d823fe', 1, 'male', 'heterosexual', 'Hello mates', '/uploads/o4eredko/large_yochered.jpg',
        '[\"/uploads/o4eredko/photo.jpeg\", \"/uploads/o4eredko/photo.jpeg\", \"\", \"/uploads/o4eredko/photo.jpeg\"]',
        18, 0, '2019-10-20 17:42:25', 'Kyiv, Ukraine'),
       (65, 'bts', 'Afrodita', 'Andriivna', 'boyetav@w6mail.com',
        'pbkdf2:sha256:150000$sOqi4NdG$293a757baa5faa4511ff5113164b8dcac180d106174095e5c284a66079d035c5',
        'af26a35b9447f0760539', 1, 'female', 'bisexual', 'Nu i sho?', '/uploads/bts/P90817-105948.jpg',
        '[\"/uploads/bts/P90817-105948.jpg\", \"\", \"\", \"\"]', 28, 0, '2019-10-10 16:47:56', 'Kyiv, Ukraine'),
       (67, 'puten', 'Putin', 'Huilo', 'femapica@2mailcloud.com',
        'pbkdf2:sha256:150000$XT1ScKrr$1ad07f23c5e5af9f9000eba031f7a7699b2af34d78ad1578c85bda4ca07178a2',
        'fa9932a32594cd4aa55d', 1, 'male', 'bisexual', 'Occupant', '/uploads/puten/puten.jpg',
        '[\"/uploads/puten/puten2.jpg\", \"\", \"\", \"\"]', 67, 1, NULL, 'Kyiv, Ukraine');


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

--
-- Дамп данных таблицы `chats`
--

INSERT INTO `chats` (`id`, `user1_id`, `user2_id`)
VALUES (1, 50, 63),
       (7, 63, 46);

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

--
-- Дамп данных таблицы `messages`
--

INSERT INTO `messages` (`id`, `chat_id`, `sender_id`, `recipient_id`, `text`)
VALUES (155, 1, 50, 63, 'Hi there!'),
       (156, 1, 50, 63, 'FFFF'),
       (157, 1, 50, 63, 'assfdasdf'),
       (158, 1, 50, 63, 'Hey?'),
       (159, 1, 50, 63, 'AAAAA'),
       (160, 1, 63, 50, 'So, why R U running?'),
       (161, 1, 63, 50, 'fadsdfsa'),
       (162, 1, 63, 50, ''),
       (163, 1, 50, 63, 'fdasfdas'),
       (164, 1, 63, 50, 'TEST'),
       (165, 1, 50, 63, 'AND YOU!'),
       (166, 1, 50, 63, 'Sooooo, it is working!'),
       (167, 1, 50, 63, 'reqwrqwerqw'),
       (168, 1, 63, 50, 'rewqrweqrqewrqew'),
       (169, 1, 63, 50, 'fdsafdasfa'),
       (170, 1, 50, 63, 'MSG'),
       (171, 1, 50, 63, 'MASSAGEEJF'),
       (172, 1, 50, 63, 'reqwrwqe'),
       (173, 1, 50, 63, 'fdas'),
       (174, 1, 63, 50, 'reqw'),
       (175, 7, 63, 46, 'Nu i sho?');

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
-- Структура таблицы `tags`
--

CREATE TABLE IF NOT EXISTS `tags`
(
    `id`   int(11)                             NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` varchar(20) COLLATE utf8_unicode_ci NOT NULL UNIQUE
) ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_unicode_ci;

--
-- Дамп данных таблицы `tags`
--

INSERT INTO `tags` (`name`)
VALUES ('sport'),
       ('history'),
       ('running'),
       ('photography'),
       ('photo'),
       ( 'programming'),
       ( 'Pivo'),
       ( 'Vodka'),
       ( 'Allah'),
       ( 'bicycle'),
       ( 'blogger'),
       ( 'Mussolini'),
       ( 'Poroshenko'),
       ( 'Football'),
       ( 'Volleyball'),
       ( 'Horilka'),
       ( 'Nichogo'),
       ( 'Burgers');

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

/*!40101 SET CHARACTER_SET_CLIENT = @OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS = @OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION = @OLD_COLLATION_CONNECTION */;

-- phpMyAdmin SQL Dump
-- version 4.8.5
-- https://www.phpmyadmin.net/
--
-- Хост: localhost
-- Время создания: Окт 20 2019 г., 18:14
-- Версия сервера: 8.0.13-4
-- Версия PHP: 7.2.19-0ubuntu0.18.04.2

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;

--
-- База данных: `matcha`
--
CREATE DATABASE IF NOT EXISTS `matcha` DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;
USE `matcha`;

-- --------------------------------------------------------

--
-- Структура таблицы `blocked`
--

CREATE TABLE `blocked` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `blocked_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Дамп данных таблицы `blocked`
--

INSERT INTO `blocked` (`id`, `user_id`, `blocked_id`) VALUES
(10, 64, 59);

-- --------------------------------------------------------

--
-- Структура таблицы `chats`
--

CREATE TABLE `chats` (
  `id` int(11) NOT NULL,
  `user1_id` int(11) NOT NULL,
  `user2_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Дамп данных таблицы `chats`
--

INSERT INTO `chats` (`id`, `user1_id`, `user2_id`) VALUES
(1, 50, 63),
(7, 63, 46);

-- --------------------------------------------------------

--
-- Структура таблицы `likes`
--

CREATE TABLE `likes` (
  `id` int(11) NOT NULL,
  `like_owner` int(11) NOT NULL,
  `liked_user` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Дамп данных таблицы `likes`
--

INSERT INTO `likes` (`id`, `like_owner`, `liked_user`) VALUES
(13, 38, 45),
(22, 44, 38),
(25, 47, 38),
(27, 38, 47),
(28, 46, 48),
(29, 48, 46),
(38, 38, 44),
(66, 38, 46),
(71, 46, 48),
(72, 46, 48),
(85, 59, 46),
(87, 61, 50),
(88, 61, 46),
(89, 61, 44),
(112, 46, 59),
(122, 50, 47),
(123, 50, 47),
(144, 46, 61),
(145, 63, 50),
(147, 50, 63),
(150, 46, 63),
(151, 50, 59),
(152, 59, 50),
(154, 63, 46);

-- --------------------------------------------------------

--
-- Структура таблицы `messages`
--

CREATE TABLE `messages` (
  `id` int(11) NOT NULL,
  `chat_id` int(11) NOT NULL,
  `sender_id` int(11) NOT NULL,
  `recipient_id` int(11) NOT NULL,
  `text` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `timestamp` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Дамп данных таблицы `messages`
--

INSERT INTO `messages` (`id`, `chat_id`, `sender_id`, `recipient_id`, `text`) VALUES
(155, 1, 50, 63, 'Hi there!'),
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

CREATE TABLE `notifications` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `message` text COLLATE utf8_unicode_ci NOT NULL,
  `link` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `viewed` tinyint(1) NOT NULL DEFAULT '0',
  `date_created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Дамп данных таблицы `notifications`
--

INSERT INTO `notifications` (`id`, `user_id`, `message`, `link`, `viewed`) VALUES
(201, 61, 'You have been unliked by afrodita', '/profile/46', 0),
(202, 61, 'You have been liked back by afrodita', '/profile/46', 0),
(203, 61, 'You have been unliked by afrodita', '/profile/46', 0),
(204, 61, 'You have been liked back by afrodita', '/profile/46', 0),
(205, 59, 'You have been liked by Jenya', '/profile/64', 0),
(206, 59, 'You have been unliked by Jenya', '/profile/64', 0),
(207, 59, 'You have been liked by Jenya', '/profile/64', 0),
(208, 59, 'Your profile was checked by Jenya', '/profile/64', 0),
(209, 59, 'You have been unliked by Jenya', '/profile/64', 0),
(210, 59, 'You have been unliked by Jenya', '/profile/64', 0),
(211, 59, 'You have been unliked by Jenya', '/profile/64', 0),
(212, 59, 'You have been unliked by Jenya', '/profile/64', 0),
(213, 59, 'You have been unliked by Jenya', '/profile/64', 0),
(214, 59, 'You have been unliked by Jenya', '/profile/64', 0),
(215, 44, 'Your profile was checked by o4eredko', '/profile/63', 0),
(216, 46, 'Your profile was checked by o4eredko', '/profile/63', 0),
(217, 46, 'You have been unliked by o4eredko', '/profile/63', 0),
(227, 63, 'Your profile was checked by afrodita', '/profile/46', 0),
(228, 59, 'You have been unliked by afrodita', '/profile/46', 0),
(229, 59, 'You have been liked back by afrodita', '/profile/46', 0),
(230, 61, 'You have been unliked by afrodita', '/profile/46', 0),
(231, 61, 'You have been liked back by afrodita', '/profile/46', 0),
(232, 61, 'You have been liked back by afrodita', '/profile/46', 0),
(233, 61, 'You have been liked back by afrodita', '/profile/46', 0),
(234, 61, 'You have been liked back by afrodita', '/profile/46', 0),
(235, 61, 'You have been liked back by afrodita', '/profile/46', 0),
(236, 61, 'You have been liked back by afrodita', '/profile/46', 0),
(237, 61, 'You have been unliked by afrodita', '/profile/46', 0),
(238, 61, 'You have been unliked by afrodita', '/profile/46', 0),
(239, 61, 'You have been liked back by afrodita', '/profile/46', 0),
(240, 61, 'You have been unliked by afrodita', '/profile/46', 0),
(241, 61, 'You have been unliked by afrodita', '/profile/46', 0),
(242, 61, 'You have been liked back by afrodita', '/profile/46', 0),
(243, 61, 'You have been liked back by afrodita', '/profile/46', 0),
(244, 47, 'You have been liked by lara', '/profile/50', 0),
(245, 47, 'You have been liked by lara', '/profile/50', 0),
(255, 61, 'You have been liked back by lara', '/profile/50', 0),
(256, 59, 'You have been liked by lara', '/profile/50', 0),
(257, 59, 'You have been unliked by lara', '/profile/50', 0),
(258, 61, 'You have been unliked by lara', '/profile/50', 0),
(259, 61, 'Your profile was checked by lara', '/profile/50', 0),
(260, 61, 'You have been liked back by lara', '/profile/50', 0),
(261, 61, 'You have been unliked by lara', '/profile/50', 0),
(262, 61, 'You have been liked back by lara', '/profile/50', 0),
(263, 61, 'You have been unliked by lara', '/profile/50', 0),
(264, 61, 'You have been liked back by lara', '/profile/50', 0),
(265, 61, 'You have been unliked by lara', '/profile/50', 0),
(266, 61, 'You have been liked back by lara', '/profile/50', 0),
(267, 61, 'You have been unliked by lara', '/profile/50', 0),
(268, 61, 'You have been liked back by lara', '/profile/50', 0),
(269, 61, 'You have been unliked by lara', '/profile/50', 0),
(270, 50, 'Your profile was checked by o4eredko', '/profile/63', 0),
(271, 50, 'You have been liked by o4eredko', '/profile/63', 0),
(272, 50, 'You have been unliked by o4eredko', '/profile/63', 0),
(273, 46, 'You have been liked by o4eredko', '/profile/63', 0),
(274, 50, 'You have been liked by o4eredko', '/profile/63', 0),
(284, 50, 'You have been unliked by o4eredko', '/profile/63', 0),
(285, 50, 'You have been liked back by o4eredko', '/profile/63', 0),
(286, 50, 'You have been unliked by o4eredko', '/profile/63', 0),
(288, 65, 'Your profile was visited by o4eredko', '/profile/63', 0),
(289, 65, 'You have been liked by o4eredko', '/profile/63', 0),
(290, 65, 'You have been unliked by o4eredko', '/profile/63', 0),
(291, 61, 'You have been unliked by afrodita', '/profile/46', 0),
(292, 61, 'You have been liked back by afrodita', '/profile/46', 0),
(309, 59, 'You have been liked by lara', '/profile/50', 0),
(310, 59, 'Your profile was visited by lara', '/profile/50', 0),
(320, 65, 'You have been liked by o4eredko', '/profile/63', 0),
(321, 65, 'You have been unliked by o4eredko', '/profile/63', 0),
(322, 46, 'You have been liked back by o4eredko', '/profile/63', 0),
(323, 46, 'You received a message from o4eredko', '/chat/63', 0);

-- --------------------------------------------------------

--
-- Структура таблицы `reports`
--

CREATE TABLE `reports` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `reported_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Дамп данных таблицы `reports`
--

INSERT INTO `reports` (`id`, `user_id`, `reported_id`) VALUES
(8, 38, 46),
(16, 64, 59),
(20, 63, 65),
(21, 63, 65),
(22, 63, 65),
(23, 63, 65),
(24, 63, 65),
(25, 63, 65),
(26, 63, 50),
(27, 63, 50);

-- --------------------------------------------------------

--
-- Структура таблицы `tags`
--

CREATE TABLE `tags` (
  `id` int(11) NOT NULL,
  `name` varchar(20) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Дамп данных таблицы `tags`
--

INSERT INTO `tags` (`id`, `name`) VALUES
(4, 'sport'),
(5, 'history'),
(6, 'running'),
(7, 'photography'),
(8, 'photo'),
(9, 'new_tag'),
(11, 'programming'),
(15, 'photos'),
(16, 'Pivo'),
(17, 'Vodka'),
(18, 'Allah'),
(19, 'bicycle'),
(20, 'blogger'),
(21, 'Sport'),
(22, 'Mussolini'),
(23, 'Poroshenko'),
(24, 'Football'),
(25, 'Volleyball'),
(26, 'Programming'),
(27, 'Horilka'),
(29, 'Nichogo'),
(30, 'Burgers');

-- --------------------------------------------------------

--
-- Структура таблицы `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `login` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `name` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `surname` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `email` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `password` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `token` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `confirmed` tinyint(1) NOT NULL DEFAULT '0',
  `gender` enum('male','female') CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `preferences` enum('bisexual','heterosexual','homosexual') CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `biography` text COLLATE utf8_unicode_ci,
  `avatar` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `photos` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL DEFAULT '["", "", "", ""]',
  `age` int(11) DEFAULT NULL,
  `online` tinyint(1) NOT NULL DEFAULT '0',
  `last_login` datetime DEFAULT NULL,
  `city` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Дамп данных таблицы `users`
--

INSERT INTO `users` (`id`, `login`, `name`, `surname`, `email`, `password`, `token`, `confirmed`, `gender`, `preferences`, `biography`, `avatar`, `photos`, `age`, `online`, `last_login`, `city`) VALUES
(44, 'login', 'Mykola', 'Kostiantynovich', 'o4eredko.crypto@gmail.com', 'pbkdf2:sha256:150000$zXhR3POx$aac96921bede1fc55dd8c3e1680541695436b1243cc463054f2d36dbdf729cfc', 'c2dfc6a5e44f3c0c8518', 1, 'female', 'bisexual', 'Are you Okay?', '/uploads/avatar.png', '[\"/uploads/afrodita/obama3.jpeg\", \"\", \"\", \"\"]', 18, 0, '2019-10-08 14:27:21', NULL),
(46, 'afrodita', 'Afrodita', 'Kardashian', 'suyuvumiwu@quickemail.info', 'pbkdf2:sha256:150000$2XeI1DDS$2757329318b832f743ba7451860425f0428472515926b423dfd96cce97006fbf', 'cefab73d61bb09d9b032', 1, 'female', 'heterosexual', 'Afganistan one love', '/uploads/avatar.png', '[\"/uploads/afrodita/obama3.jpeg\", \"\", \"uploads/afrodita/IMG_20170520_213128_785.jpg\", \"\"]', 21, 1, '2019-10-18 17:13:49', 'Kyiv, Ukraine'),
(47, 'azbek', 'Azbek', 'Farhad', 'getamazid@tempmailapp.com', 'pbkdf2:sha256:150000$9YkQ0zLb$f6662b9d4772c0150b87d1dfd5b322873b17f89ae70c59f2713676abe09dcff9', '03ac105048c7a1d87b8f', 1, 'male', 'heterosexual', 'Allah nad nami, Zemlya pod nogami', '/uploads/avatar.png', '[\"/uploads/afrodita/obama3.jpeg\", \"\", \"\", \"\"]', 35, 0, NULL, NULL),
(48, 'okherson', 'Oleksii', 'Khersoniuk', 'wufigiluse@4easyemail.com', 'pbkdf2:sha256:150000$bFKBmSHI$2a57db4514c5bfdcc821a47081f8d9dbf86dd8e6eb656d1226b4533473d92e6e', '7c4bb8564698e8bbed39', 1, 'male', 'heterosexual', NULL, '/uploads/avatar.png', '[\"/uploads/afrodita/obama3.jpeg\", \"\", \"\", \"\"]', 28, 0, NULL, NULL),
(50, 'lara', 'Larisa', 'Pindoska', 'vefatufapo@mail-point.net', 'pbkdf2:sha256:150000$wa1xr3EN$b45d57bb8983476a4a57e58db48c11a93bc686121c8213af45f23cbb753775ec', '1517e11c2286661f52d7', 1, 'female', 'heterosexual', 'Drunk as fucked', '/uploads/avatar.png', '[\"/uploads/afrodita/obama3.jpeg\", \"\", \"\", \"\"]', 18, 0, '2019-10-19 21:34:00', 'Kyiv, Ukraine'),
(59, 'maximilian', 'Maximilian', 'Moskaloder', 'wilep@inappmail.com', 'pbkdf2:sha256:150000$HjJUYSbZ$b56c68724963989061260fcfe11a76da7be93d148901a4e63ff0d3a8bd3c9c36', 'e0545d6a928ee28dd151', 1, 'male', 'bisexual', 'Hello world', '/uploads/maximilian/large_yochered.jpg', '[\"/uploads/maximilian/large_yochered.jpg\", \"\", \"uploads/maximilian/large_yochered.jpg\", \"\"]', 20, 0, '2019-10-19 16:36:34', 'Kherson, Kherson Oblast, Ukraine'),
(60, 'fdsafdas', 'Kostik', 'AAA', 'jecaxarih@my6mail.com', 'pbkdf2:sha256:150000$qptlztYP$c744f940f3f478a156b28ef559b646ced9dbd6715878b7fd89d6cef053426df8', 'd49e5fd8d4d9345ac029', 1, 'male', 'bisexual', 'AAAA', '/uploads/avatar.png', '[\"\", \"\", \"\", \"\"]', 21, 0, '2019-10-06 10:28:30', NULL),
(61, 'dzaporoz2', 'Dmytro', 'Zzzz', 'bixap@my6mail.com', 'pbkdf2:sha256:150000$Yj8mqV1b$c3b1c8a1cff69c2abb1be820a551c9b9a9ee08e8b6ff457236d46727d7493450', '6dafb79f682347a15587', 1, 'male', 'bisexual', 'biography', '/uploads/avatar.png', '[\"/uploads/dzaporoz2/1565540964.png\", \"/uploads/dzaporoz2/3.jpg\", \"\", \"\"]', 64, 0, '2019-10-06 13:07:35', 'Kyiv, Ukraine'),
(62, 'mykola', 'Mykolai', 'Saint', 'ripanoxey@app-mailer.com', 'pbkdf2:sha256:150000$VD3ld1zu$f06834980fe49046f5d5b591f384de3dc061a1f8a4bf87696e901116a7a9cffe', '14c1fb0a66cb9f59a788', 1, NULL, 'bisexual', NULL, '/static/img/default_avatar.png', '[\"\", \"\", \"\", \"\"]', 18, 0, '2019-10-06 13:08:22', NULL),
(63, 'o4eredko', 'Yevhenii', 'Ocheredko', 'evgeny.ocheredko@gmail.com', 'pbkdf2:sha256:150000$aPuxewzR$8402898026f683a27addc11db980db544c16161b188f59a739d26dbce1da6129', 'd19e412b481599d823fe', 1, 'male', 'heterosexual', 'Hello mates', '/uploads/o4eredko/large_yochered.jpg', '[\"/uploads/o4eredko/photo.jpeg\", \"/uploads/o4eredko/photo.jpeg\", \"\", \"/uploads/o4eredko/photo.jpeg\"]', 18, 0, '2019-10-20 17:42:25', 'Kyiv, Ukraine'),
(65, 'bts', 'Afrodita', 'Andriivna', 'boyetav@w6mail.com', 'pbkdf2:sha256:150000$sOqi4NdG$293a757baa5faa4511ff5113164b8dcac180d106174095e5c284a66079d035c5', 'af26a35b9447f0760539', 1, 'female', 'bisexual', 'Nu i sho?', '/uploads/bts/P90817-105948.jpg', '[\"/uploads/bts/P90817-105948.jpg\", \"\", \"\", \"\"]', 28, 0, '2019-10-10 16:47:56', 'Kyiv, Ukraine'),
(67, 'puten', 'Putin', 'Huilo', 'femapica@2mailcloud.com', 'pbkdf2:sha256:150000$XT1ScKrr$1ad07f23c5e5af9f9000eba031f7a7699b2af34d78ad1578c85bda4ca07178a2', 'fa9932a32594cd4aa55d', 1, 'male', 'bisexual', 'Occupant', '/uploads/puten/puten.jpg', '[\"/uploads/puten/puten2.jpg\", \"\", \"\", \"\"]', 67, 1, NULL, 'Kyiv, Ukraine');

-- --------------------------------------------------------

--
-- Структура таблицы `user_tag`
--

CREATE TABLE `user_tag` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `tag_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Дамп данных таблицы `user_tag`
--

INSERT INTO `user_tag` (`id`, `user_id`, `tag_id`) VALUES
(107, 47, 16),
(108, 47, 17),
(109, 47, 18),
(110, 38, 15),
(111, 38, 16),
(112, 48, 11),
(113, 48, 19),
(150, 46, 22),
(151, 61, 23),
(152, 59, 24),
(156, 63, 25),
(157, 63, 26),
(172, 65, 16),
(177, 50, 11),
(178, 50, 16),
(179, 50, 20),
(180, 50, 23),
(181, 50, 25);

-- --------------------------------------------------------

--
-- Структура таблицы `visits`
--

CREATE TABLE `visits` (
  `id` int(11) NOT NULL,
  `visitor` int(11) NOT NULL,
  `visited` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci ROW_FORMAT=COMPACT;

--
-- Дамп данных таблицы `visits`
--

INSERT INTO `visits` (`id`, `visitor`, `visited`) VALUES
(1, 38, 44),
(2, 38, 38),
(3, 38, 46),
(4, 47, 38),
(5, 38, 47),
(6, 48, 46),
(7, 46, 48),
(8, 48, 44),
(9, 46, 38),
(10, 46, 46),
(11, 50, 50),
(12, 38, 50),
(13, 46, 47),
(14, 59, 50),
(15, 59, 46),
(16, 46, 59),
(17, 61, 50),
(18, 61, 46),
(19, 46, 61),
(20, 61, 44),
(21, 62, 59),
(22, 62, 60),
(23, 62, 44),
(24, 59, 62),
(25, 59, 44),
(26, 64, 59),
(27, 63, 44),
(28, 63, 46),
(29, 46, 63),
(30, 50, 63),
(31, 50, 61),
(32, 63, 50),
(33, 63, 65),
(34, 50, 59);

--
-- Индексы сохранённых таблиц
--

--
-- Индексы таблицы `blocked`
--
ALTER TABLE `blocked`
  ADD PRIMARY KEY (`id`);

--
-- Индексы таблицы `chats`
--
ALTER TABLE `chats`
  ADD PRIMARY KEY (`id`);

--
-- Индексы таблицы `likes`
--
ALTER TABLE `likes`
  ADD PRIMARY KEY (`id`);

--
-- Индексы таблицы `messages`
--
ALTER TABLE `messages`
  ADD PRIMARY KEY (`id`);

--
-- Индексы таблицы `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`id`);

--
-- Индексы таблицы `reports`
--
ALTER TABLE `reports`
  ADD PRIMARY KEY (`id`);

--
-- Индексы таблицы `tags`
--
ALTER TABLE `tags`
  ADD PRIMARY KEY (`id`);

--
-- Индексы таблицы `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `login` (`login`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Индексы таблицы `user_tag`
--
ALTER TABLE `user_tag`
  ADD PRIMARY KEY (`id`);

--
-- Индексы таблицы `visits`
--
ALTER TABLE `visits`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT для сохранённых таблиц
--

--
-- AUTO_INCREMENT для таблицы `blocked`
--
ALTER TABLE `blocked`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT для таблицы `chats`
--
ALTER TABLE `chats`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT для таблицы `likes`
--
ALTER TABLE `likes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=155;

--
-- AUTO_INCREMENT для таблицы `messages`
--
ALTER TABLE `messages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=176;

--
-- AUTO_INCREMENT для таблицы `notifications`
--
ALTER TABLE `notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=324;

--
-- AUTO_INCREMENT для таблицы `reports`
--
ALTER TABLE `reports`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;

--
-- AUTO_INCREMENT для таблицы `tags`
--
ALTER TABLE `tags`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=33;

--
-- AUTO_INCREMENT для таблицы `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=68;

--
-- AUTO_INCREMENT для таблицы `user_tag`
--
ALTER TABLE `user_tag`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=182;

--
-- AUTO_INCREMENT для таблицы `visits`
--
ALTER TABLE `visits`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=35;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

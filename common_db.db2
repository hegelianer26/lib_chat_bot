SQLite format 3   @                                                                   .v�   0 8[0                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              �())�tablebot_statisticsbot_statisticsCREATE TABLE bot_statistics (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	category_id INTEGER, 
	action_type VARCHAR(50) NOT NULL, 
	timestamp DATETIME, 
	message_text TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(category_id) REFERENCES category (id)
)�Z�tableansweranswerCREATE TABLE answer (
	id INTEGER NOT NULL, 
	category_id INTEGER NOT NULL, 
	text TEXT NOT NULL, 
	image_path VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(category_id) REFERENCES category (id)
)�E�]tablecategorycategoryCREATE TABLE category (
	id INTEGER NOT NULL, 
	parent_id INTEGER, 
	name VARCHAR(200) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(parent_id) REFERENCES category (id)
) =���v\;�$����X|=%                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    5категория 1"  IЕЩЕ ОДНА ГЛАВНАЯ  'бля бла  5подглавная  +главная  -
подменю 4
 -	подменю 3$ Kпроверка всякого   
 10500	 -подменю 2 Aвнтури внутри  3еще внутри* Wвнутрення категория#  Kвторая категория 	-подменю 1!  Gновая категория
� 
@
�
��
@

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            ] [mдадим просто ответ 🔌uploads/e9e0a1ad-6757-40aa-a521-e2f0642fdc00.jpg% %3приветuploads/images.jpeg� #                               �V �IoВам нужно найти необходимое издание в каталоге: https://koha.lib.tsu.ru/ В поисковую строку введите название и/или автора издания. Нажав на название издания, Вы увидите место хранения экземпляра. Литература, представленная в нашем фонде, может иметь разные места хранения – Читальные залы, Книгохранилище и др. Для работы с книгами в читальном зале Вам нужен расстановочный шифр, имя автора, название издания и с этими данными пройти в соответствующий читальный зал. Если книга в книгохранилище, то её нужно предварительно заказать. Обращаем Ваше внимание, что книга должна быть «Доступна».   Если она выдана другому читателю, вы не сможете с ней поработать.uploads/57d5d364-fa9f-43f3-b615-984062d60d9c.jpeg   ' привет    '                                      �    ���                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 �-   s   ;   ; � ��A �q0 ��2��N ��?
�
i
%	�	�	L	��v(���N��O�y5��k.��D��R�tD	 � �              9;  5A �=.catalog_search_start2025-01-05 16:10:12.064217@:  9A�=.catalog_search_success2025-01-05 16:09:16.197763Lenin99  5A �=.catalog_search_start2025-01-05 16:08:59.126897.8  A �=.main_menu2025-01-05 16:08:55.106378L7  !AG�=.text_query2025-01-05 16:08:53.719398новая категорияJ6  %A?�=.failed_query2025-01-05 16:04:44.151909внтури внутриB5  !A3�=.text_query2025-01-05 16:04:42.059574еще внутриT4  !AW�=.text_query2025-01-05 16:04:40.715217внутрення категорияN3  !AK�=.text_query2025-01-05 16:04:38.540479вторая категорияJ2  %A?�=.failed_query2025-01-05 16:04:34.269770внтури внутриB1  !A3�=.text_query2025-01-05 16:04:32.979384еще внутриT0  !AW�=.text_query2025-01-05 16:04:31.917820внутрення категорияN/  !AK�=.text_query2025-01-05 16:04:30.132994вторая категория;.  %A!�=.failed_query2025-01-05 16:02:44.700579поиск.-  A �=.main_menu2025-01-05 16:02:27.015962L,  !AG�=.text_query2025-01-05 16:02:17.325620новая категорияJ+  %A?�j�failed_query2025-01-05 14:01:00.624490внтури внутриB*  !A3�j�text_query2025-01-05 14:00:58.323063еще внутриT)  !AW�j�text_query2025-01-05 14:00:55.649346внутрення категорияN(  !AK�j�text_query2025-01-05 14:00:53.229249вторая категория.'  A �j�main_menu2025-01-05 14:00:51.448264L&  !AG�j�text_query2025-01-05 13:23:53.837779новая категория=%  %A%�j�failed_query2025-01-05 13:23:39.065810Начать9$  %A�=.failed_query2025-01-05 12:52:53.942578фыва5#  %A�=.failed_query2025-01-05 12:48:27.486418asdf6"  !A�=.text_query2025-01-05 12:43:33.299309asdasdf4!  !A�=.text_query2025-01-05 12:43:03.960584\sdfg2   !A�=.text_query2025-01-05 12:43:02.692010sad6  !A�=.text_query2025-01-05 12:40:29.250602asdfasdL  !AG�=.text_query2025-01-05 12:40:27.330490новая категория3  !A�=.text_query2025-01-05 12:39:34.961496asdf2  !A�=.text_query2025-01-05 12:34:21.827180sda4  !A�=.text_query2025-01-05 12:34:01.796382mfsad5  !A�=.text_query2025-01-05 12:27:06.253897фыв?  !A-�=.text_query2025-01-05 12:03:51.017757подменю 1L  !AG�=.text_query2025-01-05 12:03:48.270110новая категорияH  !A?�=.text_query2025-01-05 12:03:38.835649внтури внутриB  !A3�=.text_query2025-01-05 12:01:02.606556еще внутриT  !AW�=.text_query2025-01-05 12:01:01.545492внутрення категорияN  !AK�=.text_query2025-01-05 12:01:00.633319вторая категория.  A �=.main_menu2025-01-05 12:00:59.900552N  !AK�=.text_query2025-01-05 12:00:58.919358вторая категория.  A �=.main_menu2025-01-05 12:00:57.454004?  !A-�=.text_query2025-01-05 12:00:55.164119подменю 1L  !AG�=.text_query2025-01-05 12:00:11.712889новая категорияH  !A?�=.text_query2025-01-05 11:56:54.723593внтури внутриB  !A3�=.text_query2025-01-05 11:56:53.361405еще внутриT  !AW�=.text_query2025-01-05 11:56:52.028685внутрення категорияN  !AK�=.text_query2025-01-05 11:56:50.465647вторая категория.
  A �=.main_menu2025-01-05 11:56:48.618976L	  !AG�=.text_query2025-01-05 11:56:47.321891новая категория.  A �=.main_menu2025-01-05 11:55:53.552976?  !A-�=.text_query2025-01-05 11:55:45.473919подменю 1?  !A-�=.text_query2025-01-05 11:48:45.577474подменю 1L  !AG�=.text_query2025-01-05 11:48:42.931171новая категория?  !A-�=.text_query2025-01-05 11:48:06.314062подменю 1?  !A-�=.text_query2025-01-05 11:40:29.500389подменю 1L  !AG�=.text_query2025-01-05 11:40:27.385169новая категория.  A �=.main_menu2025-01-05 11:35:47.005361   8 � �n3��T��:��}M��O
�
�

/	�	�	[	+��5��U��o!��K�m=��m,��V�vF � �                                        Ts  !AW�=.text_query2025-01-06 14:55:12.401938внутрення категорияNr  !AK�=.text_query2025-01-06 14:55:10.853188вторая категория.q  A �=.main_menu2025-01-06 14:55:09.946008Np  !AK�=.text_query2025-01-06 14:55:04.814239вторая категорияJo  %A?�=.failed_query2025-01-06 14:53:39.074996внтури внутриBn  !A3�=.text_query2025-01-06 14:53:18.681165еще внутриTm  !AW�=.text_query2025-01-06 14:53:17.598641внутрення категорияNl  !AK�=.text_query2025-01-06 14:53:13.557139вторая категория.k  A �=.main_menu2025-01-06 14:53:12.643815?j  !A-�=.text_query2025-01-06 14:53:02.772099подменю 4?i  !A-�=.text_query2025-01-06 14:53:01.250419подменю 3?h  !A-�=.text_query2025-01-06 14:52:59.385147подменю 2Lg  !AG�=.text_query2025-01-06 14:52:53.388383новая категория.f  A �=.main_menu2025-01-06 14:50:48.424667Le  !AG�=.text_query2025-01-06 14:48:49.428070новая категорияJd  %A?�=.failed_query2025-01-06 14:46:09.811654внтури внутриBc  !A3�=.text_query2025-01-06 14:46:07.377123еще внутриTb  !AW�=.text_query2025-01-06 14:46:06.196420внутрення категорияNa  !AK�=.text_query2025-01-06 14:43:35.262873вторая категория.`  A �=.main_menu2025-01-06 14:43:34.267773L_  !AG�=.text_query2025-01-06 05:49:12.240606новая категорияJ^  %A?�=.failed_query2025-01-06 05:11:57.425942внтури внутриB]  !A3�=.text_query2025-01-06 05:11:55.573783еще внутриT\  !AW�=.text_query2025-01-06 05:11:54.515780внутрення категорияN[  !AK�=.text_query2025-01-06 05:11:50.274787вторая категорияJZ  %A?�=.failed_query2025-01-06 04:58:54.962986внтури внутриBY  !A3�=.text_query2025-01-06 04:58:53.321736еще внутриTX  !AW�=.text_query2025-01-06 04:58:51.939298внутрення категорияNW  !AK�=.text_query2025-01-06 04:58:42.565408вторая категорияNV  !AK�=.text_query2025-01-06 04:47:55.386243вторая категория.U  A �=.main_menu2025-01-06 04:47:54.308051LT  !AG�=.text_query2025-01-06 04:47:48.931265новая категория.S  A �=.main_menu2025-01-06 04:47:46.833465TR  !AW�=.text_query2025-01-06 04:30:12.381288внутрення категорияNQ  !AK�=.text_query2025-01-06 04:30:07.901729проверка всякогоNP  !AK�=.text_query2025-01-06 04:30:05.097431вторая категория.O  A �=.main_menu2025-01-06 04:29:31.494731NN  !AK�=.text_query2025-01-06 04:18:39.235659вторая категория.M  A �=.main_menu2025-01-05 18:04:20.816683NL  !AK�=.text_query2025-01-05 18:04:18.183858вторая категория.K  A �=.main_menu2025-01-05 18:03:46.135297LJ  !AG�=.text_query2025-01-05 17:39:00.108919новая категория.I  A �=.main_menu2025-01-05 17:38:58.1367679H  5A �=.catalog_search_start2025-01-05 17:38:56.123384EG  9A!�=.catalog_search_success2025-01-05 16:27:34.250066Tomsk city9F  5A �=.catalog_search_start2025-01-05 16:27:15.670092PE  9A7�=.catalog_search_success2025-01-05 16:16:56.557154war and peace Tolstoy9D  5A �=.catalog_search_start2025-01-05 16:16:47.744208PC  9A7�=.catalog_search_success2025-01-05 16:16:12.803361war and peace Tolstoy9B  5A �=.catalog_search_start2025-01-05 16:16:05.002454PA  9A7�=.catalog_search_success2025-01-05 16:11:57.479493war and peace Tolstoy9@  5A �=.catalog_search_start2025-01-05 16:11:42.915410P?  9A7�=.catalog_search_success2025-01-05 16:10:54.273173war and peace Tolstoy9>  5A �=.catalog_search_start2025-01-05 16:10:45.646431F=  %A7�=.failed_query2025-01-05 16:10:40.177325war and peace TolstoyH<  9A'�=.catalog_search_success2025-01-05 16:10:21.186704war and peace   : � �p ��:��l<��Q��@
�
�
z
8	�	�	x	G	��4��K��^��K	��V��^-��\+��x! � �                   J�-  %A?�=.failed_query2025-01-09 16:45:43.289410внтури внутриB�,  !A3�=.text_query2025-01-09 16:45:41.886710еще внутриT�+  !AW�=.text_query2025-01-09 16:45:40.723773внутрення категорияN�*  !AK�=.text_query2025-01-09 16:45:35.018053вторая категория.�)  A �=.main_menu2025-01-09 16:45:19.360321.�(  A �=.main_menu2025-01-09 16:44:58.887760.�'  A �=.main_menu2025-01-09 16:44:43.382635M�&  !AI�=.text_query2025-01-09 16:44:41.626475ЕЩЕ ОДНА ГЛАВНАЯ.�%  A �=.main_menu2025-01-09 16:01:21.553690M�$  !AI�=.text_query2025-01-09 16:01:19.765768ЕЩЕ ОДНА ГЛАВНАЯ.�#  A �=.main_menu2025-01-06 17:43:50.8035044�"  !A�=.text_query2025-01-06 17:43:47.32700110500M�!  !AI�=.text_query2025-01-06 17:43:45.966406ЕЩЕ ОДНА ГЛАВНАЯ.�   A �=.main_menu2025-01-06 17:43:44.520850=�  !A)�=.text_query2025-01-06 17:43:43.399745раздел 1?�  %A)�=.failed_query2025-01-06 16:14:07.653121главная.�  A �=.main_menu2025-01-06 16:13:13.525460=�  !A)�=.text_query2025-01-06 16:13:11.737678раздел 1?�  %A)�=.failed_query2025-01-06 16:13:06.760258главная?�  %A)�=.failed_query2025-01-06 16:12:33.727919главная?�  %A)�=.failed_query2025-01-06 16:11:08.833600главная?�  %A)�=.failed_query2025-01-06 16:10:51.560589главнаяJ�  %A?�=.failed_query2025-01-06 16:10:13.228136внтури внутриB�  !A3�=.text_query2025-01-06 16:10:11.979921еще внутриT�  !AW�=.text_query2025-01-06 16:10:10.730515внутрення категорияN�  !AK�=.text_query2025-01-06 16:10:08.382524вторая категорияJ�  %A?�=.failed_query2025-01-06 16:09:34.082141внтури внутриB�  !A3�=.text_query2025-01-06 16:09:33.149484еще внутриT�  !AW�=.text_query2025-01-06 16:09:31.988124внутрення категорияN�  !AK�=.text_query2025-01-06 16:09:30.301153вторая категория.�  A �=.main_menu2025-01-06 16:09:28.366581L�  !AG�=.text_query2025-01-06 15:53:33.755673новая категория?�  %A)�=.failed_query2025-01-06 15:53:18.711446главная.�  A �=.main_menu2025-01-06 15:53:17.004055L�  !AG�=.text_query2025-01-06 15:34:26.955264новая категория.�
  A �=.main_menu2025-01-06 15:23:32.661147=�	  !A)�=.text_query2025-01-06 15:23:30.784012раздел 1?�  %A)�=.failed_query2025-01-06 15:23:29.195069главная?�  %A)�=.failed_query2025-01-06 15:23:06.136749главная?�  %A)�=.failed_query2025-01-06 15:23:03.736418главная?�  %A)�=.failed_query2025-01-06 15:22:39.214358главная?�  %A)�=.failed_query2025-01-06 15:22:36.260081главная.�  A �=.main_menu2025-01-06 15:22:34.760239N�  !AK�=.text_query2025-01-06 15:22:33.358703вторая категорияJ�  %A?�=.failed_query2025-01-06 15:21:02.762332внтури внутриB�   !A3�=.text_query2025-01-06 15:21:01.758486еще внутриT  !AW�=.text_query2025-01-06 15:21:00.647389внутрення категорияN~  !AK�=.text_query2025-01-06 15:20:59.473861вторая категория.}  A �=.main_menu2025-01-06 15:20:58.277587N|  !AK�=.text_query2025-01-06 15:20:55.397943вторая категория.{  A �=.main_menu2025-01-06 15:20:54.558952Lz  !AG�=.text_query2025-01-06 15:19:43.526438новая категорияJy  %A?�=.failed_query2025-01-06 15:19:41.896899внтури внутриBx  !A3�=.text_query2025-01-06 15:19:40.754280еще внутриTw  !AW�=.text_query2025-01-06 15:19:39.706356внутрення категорияNv  !AK�=.text_query2025-01-06 15:19:33.499455вторая категорияJu  %A?�=.failed_query2025-01-06 14:55:15.022879внтури внутриBt  !A3�=.text_query2025-01-06 14:55:13.721714еще внутри   i �b��`$��B�i                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       T�:  !AW�=.text_query2025-01-10 14:10:35.794190внутрення категорияN�9  !AK�=.text_query2025-01-10 14:10:34.716563вторая категория.�8  A �=.main_menu2025-01-10 14:10:33.339555M�7  !AI�=.text_query2025-01-10 13:57:49.199493ЕЩЕ ОДНА ГЛАВНАЯL�6  !AG�=.text_query2025-01-10 13:28:01.875793новая категория@�5  9A�=.catalog_search_success2025-01-09 16:51:08.049248Lenin9�4  5A �=.catalog_search_start2025-01-09 16:51:01.021279.�3  A �=.main_menu2025-01-09 16:50:59.719362L�2  !AG�=.text_query2025-01-09 16:50:51.324308новая категория.�1  A �=.main_menu2025-01-09 16:50:50.245587N�0  !AK�=.text_query2025-01-09 16:50:46.272999вторая категорияL�/  !AG�=.text_query2025-01-09 16:46:43.985772новая категорияL�.  !AG�=.text_query2025-01-09 16:45:46.544513новая категория
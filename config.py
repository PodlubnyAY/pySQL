TP_NIR_HEADERS = ('Код ВУЗа', 'Рег. номер НИР', 'Характер НИР', 'Сокр. назв. ВУЗа',
                  'Код ГРНТИ', 'Руководитель НИР', 'Должность руководителя',
                  'Плановое финанс.', 'Наименование НИР')
GRNTI_HEADERS = ('Код рубрики', 'Рубрика')
TP_FV_HEADERS = ('Код ВУЗа', 'Сокр. назв. ВУЗА', 'Плановое финанс.',
                 'Фактическое финанс.', 'Кол-во НИР')
VUZ_HEADERS = ('Код ВУЗа', 'Сокр. назв. ВУЗа', 'Статус', 'Фед. округ', 'Город',
               'Код области', 'Субъект Федерации', 'Научный статус',
               'Проф. направление', 'Наименование ВУЗа', 'Полное наименование ВУЗа')
# original headers ['codvuz', 'z2', 'status', 'region', 'city', 'obl', 'oblname', 'gr_ved', 'prof', 'z1', 'z1full']
GRNTI_COLUMN_WIDTH = (100, 550)
TP_NIR_COLUMN_WIDTH = (80, 120, 120, 130, 140, 150, 180, 140, 100)
TP_FV_COLUMN_WIDTH = (80, 130, 140, 150, 100)
VUZ_COLUMN_WIDTH = (80, 130, 120, 130, 140, 100, 200, 140, 100, 700, 1000)

widgetnames = ['Financial', 'Vuz', 'Grnti', 'Nir']

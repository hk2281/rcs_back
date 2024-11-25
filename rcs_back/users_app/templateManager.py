from dataclasses import dataclass, field
from functools import wraps
from pathlib import Path
import random
import string

from .models import MJMLTemplate

def generate_random_id():
    return ''.join(random.choices(string.ascii_letters, k=8))

@dataclass
class JinjaBlock:
    name:str = ''
    content:str = ''


@dataclass
class Template:
    path:str
    name: str
    description: str
    mjml_template: str | None = None
    html_template: str | None = None
    if_statement: bool = False
    for_statement: bool = False
    template_id:str = field(default_factory=generate_random_id)
    hide_containers: list[tuple[JinjaBlock]] = field(default_factory=list)
    shown_containers: list[JinjaBlock] = field(default_factory=list)

    def as_dict(self):
        return {
            "path": self.path,
            "name": self.name,
            "description": self.description,
            "mjml_template": self.mjml_template,
            "html_template": self.html_template,
            "if_statement": self.if_statement,
            "for_statement": self.for_statement,
            "template_id": self.template_id,
            "hide_containers": [
                [block.__dict__ for block in container]
                for container in self.hide_containers
            ],
            "shown_containers": [
                {"name": block.name, "content": block.content}
                for block in self.shown_containers
            ],
        }


class MailTemplateManager():
    def __init__(self) -> None:
        self._current_template:str = None

        self.templates_data: dict[str,Template] = {
            'container_activation_request': 
                Template(
                    path='containers_app/templates',
                    name="container_activation_request.html",
                    shown_containers=[
                        JinjaBlock(name='id контейнера',content='{{ container.pk }}'),
                        JinjaBlock(name='масса контейнера', content="{{ container.mass }}"),
                        JinjaBlock(name='адресс здания в котором расположен контейнер',content='{{ container.building.address }}'),
                        JinjaBlock(name='этаж контейнера',content='{{ container.floor}}'),
                        JinjaBlock(name='аудитория с контейнером',content='{{ container.room }}'),
                        JinjaBlock(name='телефон ответственного',content='{{container.phone}}'), 
                        JinjaBlock(name='email ответственного',content='{{container.email}}'),
                        JinjaBlock(name='описание',content='{{ container.description }}')],
                    description='этот шаблон отвечает за активацию контейнера',
                    mjml_template='',
                ),
            'public_container_add':
                Template(
                    path='containers_app/templates',
                    name='public_container_add.html',
                    shown_containers=[
                        JinjaBlock(name='условие проверяющее является ли контейнер экобоксом',content='{% if is_ecobox %}'),
                        JinjaBlock(name='аудитория с контейнером',content='{{ container_room }}'),
                        JinjaBlock(name='else блок',content="{% else %}"),
                        JinjaBlock(name='конец if блока ',content="{% endif %}"),
                        JinjaBlock(name='номер аудитории в которой выдают стикеры',content='{{ sticker_room }}'),
                        JinjaBlock(name='ФИО ответственного за выдачу стикера',content='{{ sticker_giver }}')
                    ],
                    description='шаблон добавления нового публичного контейнера',
                    mjml_template='',
                    if_statement=True,
                ),
            'public_feedback': 
                Template(
                    path='containers_app/templates',
                    name='public_feedback.html',
                    shown_containers=[
                        JinjaBlock(name='начало if блока',content='{% if container_id %}'),
                        JinjaBlock(name='id контейнера',content='{{ container_id }}'),
                        JinjaBlock(name='конец блока if',content='{%endif%}'),
                        JinjaBlock(name='сообщение пользователя', content='{{ msg }}')
                    ],
                    description='публичный отзыв',
                    mjml_template='',
                    if_statement=True,
                ),
            'tank_takeout':
                Template(
                    path='takeouts_app/templates',
                    name="tank_takeout.html",
                    shown_containers=[
                        JinjaBlock(name='адрес здания из которого необходимо произвести вывоз', content='{{address}}'),
                        JinjaBlock(name='почта ответственного хоз работника', content='{{email}}'),
                        JinjaBlock(name='телефон работника', content='{{phone}}'),
                        JinjaBlock(name='ФИО работника', content='{{name}}')

                    ],
                    description='оповещение о организованном вывозе'
                ),
            'takeout_condition_met':
                Template(
                    path='takeouts_app/templates',
                    name='takeout_condition_met.html',
                    shown_containers=[
                        JinjaBlock(name='адрес здания в котором необходимо произвести сбор', content='{{ address }}'),
                        JinjaBlock(name='условие для отображения корпуса, начало if блока', content='{% if has_building_parts %}'),
                        JinjaBlock(name='конец if блока', content='{% endif %}'),
                        JinjaBlock(name='начало for цикла для перебора контейнеров', content='{% for container in containers %}'),
                        JinjaBlock(name='номер помещения контейнера', content='{{ container.room }}'),
                        JinjaBlock(name='номер корпуса необходимо поместить в if условие', content='{{ container.building_part.num }}'),
                        JinjaBlock(name='этаж на котором находится контейнер', content='{{ container.floor }}'),
                        JinjaBlock(name='id контейнера', content='{{ container.pk }}'),
                        JinjaBlock(name='отображение вида', content='{{ container.get_kind_display}}'),
                        JinjaBlock(name='описание', content='{{ container.description }}'),
                        JinjaBlock(name='конец for блока', content='{% endfor %}'),
                        JinjaBlock(name='дата дедлайна по сбору контейнера', content='{{ due_date }}'),
                        JinjaBlock(name='ссылка для организации групового сбора контейнеров', content='{{ link }}'),
                    ],
                    description='шаблон уведомляющий о необходимости сбора контейнеров',
                    if_statement=True
                ),
            'containers_for_takeout':
                Template(
                    path='takeouts_app/templates',
                    name='containers_for_takeout.html',
                    shown_containers=[
                        JinjaBlock(name='условие для отображения корпуса, начало if блока', content='{% if has_building_parts %}'),
                        JinjaBlock(name='номер помещения контейнера', content='{{ container.room }}'),
                        JinjaBlock(name='конец if блока', content='{% endif %}'),
                        JinjaBlock(name='начало for цикла для перебора контейнеров', content='{% for container in containers %}'),
                        JinjaBlock(name='конец for блока', content='{% endfor %}'),
                        JinjaBlock(name='номер корпуса необходимо поместить в if условие', content='{{ container.building_part.num }}'),
                        JinjaBlock(name='этаж на котором находится контейнер', content='{{ container.floor }}'),
                        JinjaBlock(name='id контейнера', content='{{ container.pk }}'),
                        JinjaBlock(name='отображение вида', content='{{ container.get_kind_display}}'),
                        JinjaBlock(name='описание', content='{{ container.description }}'),
                    ],
                    description='шаблон перечисляющий контейнеры в сборе',
                    if_statement=True
                ),
            'collected_mass_mailing':
                Template(
                    path='takeouts_app/templates',
                    name='collected_mass_mailing.html',
                    shown_containers=[
                        JinjaBlock(name='дата начала', content='{{start_date}}'),
                        JinjaBlock(name='дата окончания', content='{{end_date}}'),
                        JinjaBlock(name='масса в кг сколько было собрано за текущий период', content='{{total_mass}}'),
                        JinjaBlock(name='в вашем здании было собрано кг', content='{{building_mass}}'),
                        JinjaBlock(name='Вы и ваши коллеги по офису накопили за это время', content='{{container_mass}}'),
                        JinjaBlock(name='контейнер id', content='{{container_ids}}'),
                        JinjaBlock(name='процент показывающий на сколько было собрано больше относительно других держателей контейнеров', content='{{percentage}}')
                    ],
                    description='шаблон подведения итогов за квартал',

                ),
            'archive_takeout': 
                Template(
                    path='takeouts_app/templates',
                    name='archive_takeout.html',
                    shown_containers=[
                        JinjaBlock(name='адрес для сбора архива', content='{{address}}'),
                        JinjaBlock(name='аудитория архива', content='{{room}}'),
                        JinjaBlock(name='запрос поступил от email', content='{{email}}'),
                        JinjaBlock(name='телефон для связи', content='{{phone}}'),
                        JinjaBlock(name='дополнительная информация', content='{{description}}'),
                        JinjaBlock(name='дата дедлайна для сбора мукулатуры', content='{{ due_date }}')
                    ],
                    description='шаблон для уведомления сбора архива'
                    
                )
            }
        
    @property
    def current_template(self) -> str|None:
        return self._current_template

    @current_template.setter
    def current_template(self, template_name:str):
        if not self.templates_data.get(template_name):
            raise KeyError("стандартного шаблона с таким именем нет")
        self._current_template = template_name

    def get_bace_mjml(self)-> str:
        return """
        <mjml>
            <mj-body>
            
            </mj-body>
        </mjml>
                """

    def get_all_templates(self) -> list[dict[any]]:
        '''метод для получения списка шаблонов на фронт'''
        data = []
        templates = MJMLTemplate.objects.all()
        templates = {template.name: template for template in templates}
        for key, val in self.templates_data.items():
            mjml_from_db = templates.get(val.name, '')
            try:
                mjml_from_db = mjml_from_db.mjml_content
            except: 
                mjml_from_db = ''
            data.append({
                'id': val.template_id,
                'label': val.description,
                'media': key,
                'content':[block.__dict__ for block in val.shown_containers],
                'description': val.description,
                'mjml_template': mjml_from_db if mjml_from_db else self.get_bace_mjml()
            })
        return data

    def get_mjml_from_db(self,mjml_name:str) -> str:
        '''метод для получения mjml шаблона из бд'''
        ...
        if mjml_name == 'kek':
            return 'rigth'


    def html_extender(self, row_template:str) -> str:
        '''метод для того чтобы добавить неотображенные контейнеры jinja'''
        ...
        templates = self.templates_data[self._current_template].hide_containers
        result = row_template
        for template in reversed(templates):
            if isinstance(template, tuple):

                result = f"{template[0].content}\n{result}\n{template[1].content}"

        
        return result.strip()


    def save(self, data:dict):
        '''метод для сохранения шаблона'''
        BASE_PATH = Path(__file__).resolve().parent.parent
        template = self.templates_data.get(self.current_template)
        save_path = BASE_PATH / template.path / template.name
        # final_template = self.html_extender(data)
        final_template = data.get("mjml_template")

         # Проверяем, существует ли шаблон с таким именем в базе данных
        existing_template = MJMLTemplate.objects.filter(name=template.name).first()

        if existing_template:
            # Если шаблон существует, обновляем его содержимое
            existing_template.mjml_content = final_template
            existing_template.save()
            print(f'Обновлен шаблон с именем {template.name}')
        else:
            # Если шаблон не существует, создаем новый
            new_template = MJMLTemplate.objects.create(
                name=template.name,
                mjml_content=final_template
            )
        print(f'Создан новый шаблон с именем {template.name}')
    
        # Сохраняем шаблон на диске
        with open(save_path, 'w') as file:
            file.write(data.get('html_template'))

        print(f'сохранили по пути {save_path}, шаблон {final_template}')

    def get_template(self, template_name) -> dict:
        self.current_template = template_name
        template = self.templates_data.get(template_name)
        template.mjml_template = self.get_mjml_from_db(mjml_name='kek')
        return template.as_dict()


def default_factory():
    return MailTemplateManager()


class ServiceProvider:
    def __init__(self, create_instance=default_factory):
        self.create_instance = create_instance

    _instance = None

    @property
    def MailTemplateServise(self) -> MailTemplateManager:
       if self._instance:
           print('отдаем созданный объект')
           return self._instance
       print('создаем новый')
       self._instance = self.create_instance()
       return self._instance

service_provider = ServiceProvider()


if __name__ == '__main__': 
    manager = MailTemplateManager()
    print(manager.get_template('public_feedback'))
    pass
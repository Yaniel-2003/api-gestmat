import random
from django.core.management.base import BaseCommand
from faker import Faker
from django.contrib.auth.hashers import make_password
from django.db import transaction

# Importar modelos
from usuarios.models import Tipo_documento, Perfil, Usuario
from academico.models import Eps, Jornada, Curso, Acudiente, Estudiante
from matriculas.models import Matricula

class Command(BaseCommand):
    help = 'Genera datos de prueba masivos para GestMat usando Faker'

    def add_arguments(self, parser):
        parser.add_argument('--cantidad', type=int, default=1000, help='Cantidad de registros a generar')

    @transaction.atomic
    def handle(self, *args, **kwargs):
        cantidad = kwargs['cantidad']
        fake = Faker('es_CO')
        
        self.stdout.write(self.style.SUCCESS(f'Iniciando la generación de {cantidad} registros de prueba...'))

        # 1. Crear Perfil base
        perfil, _ = Perfil.objects.get_or_create(nombre_perfil='EstudianteTest', defaults={'estado': True})
        perfil_acudiente, _ = Perfil.objects.get_or_create(nombre_perfil='AcudienteTest', defaults={'estado': True})
        
        # 2. Crear Tipos de Documento base
        tipo_doc, _ = Tipo_documento.objects.get_or_create(descripcion='Cédula de Ciudadanía', sigla='CC')
        tipo_doc_ti, _ = Tipo_documento.objects.get_or_create(descripcion='Tarjeta de Identidad', sigla='TI')

        # 3. Crear EPS base
        eps_list = []
        for nombre in ['Sura', 'Sanitas', 'Compensar', 'Salud Total', 'Nueva EPS']:
            e, _ = Eps.objects.get_or_create(nombre_eps=nombre)
            eps_list.append(e)

        # 4. Crear Jornadas base
        jornada_m, _ = Jornada.objects.get_or_create(nombre_jornada='Mañana')
        jornada_t, _ = Jornada.objects.get_or_create(nombre_jornada='Tarde')

        # 5. Crear Cursos base
        cursos_list = []
        for i in range(1, 12):
            c, _ = Curso.objects.get_or_create(
                nombre_curso=f'Grado {i}',
                grado=str(i),
                jornada=random.choice([jornada_m, jornada_t]),
                defaults={'cupo_total': 10000, 'cupo_disponible': 10000}
            )
            cursos_list.append(c)

        # Pre-generar un acudiente para agrupar estudiantes (ej. 1 acudiente por cada 2 estudiantes)
        acudientes_creados = []
        self.stdout.write('Generando Acudientes...')
        for _ in range(cantidad // 2):
            nombre_ac = fake.name()
            # Asegurar longitud correcta
            username_ac = fake.unique.user_name()[:15]
            user_ac = Usuario.objects.create(
                username=username_ac,
                first_name=nombre_ac.split()[0][:30],
                last_name=' '.join(nombre_ac.split()[1:])[:30],
                email=fake.unique.email()[:50],
                password=make_password('TestPassword123'),
                perfil=perfil_acudiente,
                tipo_documento=tipo_doc,
                num_documento=fake.unique.ssn()[:20]
            )
            ac = Acudiente.objects.create(
                tipo_documento=tipo_doc,
                usuario=user_ac,
                numero_documento=user_ac.num_documento,
                nombre_completo=nombre_ac[:100],
                parentesco=random.choice(['Padre', 'Madre', 'Tío/a', 'Abuelo/a']),
                telefono=fake.phone_number()[:15],
                email=user_ac.email
            )
            acudientes_creados.append(ac)

        # 6. Generar Estudiantes y Matrículas
        self.stdout.write('Generando Estudiantes y Matrículas...')
        for i in range(cantidad):
            nombre_est = fake.name()
            username_est = fake.unique.user_name()[:15]
            user_est = Usuario.objects.create(
                username=username_est,
                first_name=nombre_est.split()[0][:30],
                last_name=' '.join(nombre_est.split()[1:])[:30],
                email=fake.unique.email()[:50],
                password=make_password('TestPassword123'),
                perfil=perfil,
                tipo_documento=tipo_doc_ti,
                num_documento=fake.unique.ssn()[:20]
            )
            est = Estudiante.objects.create(
                tipo_documento=tipo_doc_ti,
                eps=random.choice(eps_list),
                numero_documento=user_est.num_documento,
                nombre_completo=nombre_est[:100],
                fecha_nacimiento=fake.date_of_birth(minimum_age=5, maximum_age=18)
            )
            # Asignar un acudiente
            acudiente_asignado = random.choice(acudientes_creados)
            est.acudientes.add(acudiente_asignado)
            
            # Crear matrícula
            Matricula.objects.create(
                estudiante=est,
                acudiente=acudiente_asignado,
                curso=random.choice(cursos_list),
                jornada=random.choice([jornada_m, jornada_t]),
                year_lectivo=2024,
                estado=True,
                observaciones='Matrícula generada automáticamente para pruebas'
            )
            if i % 100 == 0:
                self.stdout.write(f'... {i} registros procesados')

        self.stdout.write(self.style.SUCCESS(f'Generación completada exitosamente! {cantidad} registros de prueba creados.'))

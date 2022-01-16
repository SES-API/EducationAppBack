from .models import *
from django.db.models import Avg, Max, Min
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from class_app.models import ClassStudents


def count_graded_question(question):
    student_num = question.assignment_id.class_id.students.all().count()
    grades_num = Grade.objects.filter(question_id=question).exclude(value=None).count()
    not_graded = student_num - grades_num
    if(not_graded<0):
        not_graded = 0
    question.not_graded_count = not_graded

    if not_graded > 0:
        question.is_graded = False
    else:
        question.is_graded = True
    
    question.save()


def count_graded_assignment(assignment):
    not_graded = 0
    for question in assignment.assignment_question.all():
        if question.is_graded == False:
            not_graded += 1
    assignment.not_graded_count = not_graded

    if not_graded == 0:
        assignment.is_graded = True
    else:
        assignment.is_graded = False

    assignment.save()


def calculate_assignment_grades(assignment, student):
    has_asg_grade = True
    val=0
    valuesum=0
    totalsum=0
    for q in assignment.assignment_question.all():
        q_grade = q.question_grade.filter(user_id=student)
        if(q_grade and q_grade.first().final_grade):
            valuesum+=q_grade.first().final_grade
            totalsum+=q.full_grade
        # else:
            # has_asg_grade = False
    if(totalsum != 0):
        val=round( ((valuesum*100)/totalsum), 2)
    else:
        val=None

    if(has_asg_grade):
        assignment_grade = AssignmentGrade.objects.filter(assignment_id=assignment, user_id=student)
        if(assignment_grade):
            assignment_grade= assignment_grade.first()
            assignment_grade.value = val
            assignment_grade.save()
        else:
            AssignmentGrade.objects.create(assignment_id=assignment, user_id=student, value=val)
    else:
        assignment_grade = AssignmentGrade.objects.filter(assignment_id=assignment, user_id=student).first()
        assignment_grade.value = None
        assignment_grade.save()


def calculate_assignment_properties(assignment):
    asg_min_grade = AssignmentGrade.objects.filter(assignment_id=assignment).exclude(value=None).aggregate(Min('value'))['value__min']
    if(asg_min_grade):
        assignment.min_grade = round(asg_min_grade, 2)
    else:
        assignment.min_grade = None
    asg_max_grade = AssignmentGrade.objects.filter(assignment_id=assignment).exclude(value=None).aggregate(Max('value'))['value__max']
    if(asg_max_grade):
        assignment.max_grade = round(asg_max_grade, 2)
    else:
        assignment.max_grade = None
    asg_avg_grade = AssignmentGrade.objects.filter(assignment_id=assignment).exclude(value=None).aggregate(Avg('value'))['value__avg']
    if(asg_avg_grade):
        assignment.avg_grade = round(asg_avg_grade, 2)
    else:
        assignment.avg_grade = None
    assignment.save()


def calculate_class_grades(class_, student):
    has_cls_grade = True
    val=0
    valuesum=0
    totalsum=0
    for asg in class_.assignment_class.all():
        totalsum+=asg.weight
        asg_grade = asg.assignment_grade.filter(user_id=student)
        if(asg_grade and asg_grade.first().value):
            valuesum+=(asg_grade.first().value * asg.weight)
        else:
            has_cls_grade = False
    val=round( (valuesum/totalsum), 2)

    if(has_cls_grade):
        cls_grade = ClassGrade.objects.filter(class_id=class_, user_id=student)
        if(cls_grade):
            cls_grade = cls_grade.first()
            cls_grade.value = val
            cls_grade.save()
        else:
            ClassGrade.objects.create(class_id=class_, user_id=student, value=val)
    else:
        cls_grade = ClassGrade.objects.filter(class_id=class_, user_id=student).first()
        cls_grade.value = None
        cls_grade.save()


def calculate_question_properties(question):
    q_min_grade = Grade.objects.filter(question_id=question).exclude(final_grade=None).aggregate(Min('final_grade'))['final_grade__min']
    if(q_min_grade):
        question.min_grade = round(q_min_grade, 2)
    else:
        question.min_grade = None
    q_max_grade = Grade.objects.filter(question_id=question).exclude(final_grade=None).aggregate(Max('final_grade'))['final_grade__max']
    if(q_max_grade):
        question.max_grade = round(q_max_grade, 2)
    else:
        question.max_grade = None
    q_avg_grade = Grade.objects.filter(question_id=question).exclude(final_grade=None).aggregate(Avg('final_grade'))['final_grade__avg']
    if(q_avg_grade):
        question.avg_grade = round(q_avg_grade, 2)
    else:
        question.avg_grade = None
    question.save()



#-------------------------signals:


@receiver(post_save, sender=ClassStudents)
def student_num_changed(sender, **kwargs):
    class_ = kwargs['instance'].Class
    user_id = kwargs['instance'].student
    assignments = Assignment.objects.filter(class_id = class_)
    for assignment in assignments:
        questions = Question.objects.filter(assignment_id = assignment)
        for question in questions:
            Grade.objects.create(user_id=user_id, question_id=question, value=None, delay=None, final_grade=None)
            question.not_graded_count += 1
            question.is_graded = False
        AssignmentGrade.objects.create(user_id=user_id, assignment_id=assignment, value=None)
        assignment.not_graded_count = assignment.assignment_question.all().count()
        assignment.is_graded = False
    ClassGrade.objects.create(user_id=user_id, class_id=class_, value=None)



@receiver(post_delete, sender=ClassStudents)
def student_num_changed(sender, **kwargs):
    class_ = kwargs['instance'].Class
    user_id = kwargs['instance'].student
    assignments = Assignment.objects.filter(class_id = class_)
    for assignment in assignments:
        questions = Question.objects.filter(assignment_id = assignment)
        for question in questions:
            grade = Grade.objects.filter(user_id=user_id, question_id=question).first()
            if(grade):
                grade.delete()
            count_graded_question(question)
        asg_grade = AssignmentGrade.objects.filter(user_id=user_id, assignment_id=assignment).first()
        if(asg_grade):
            asg_grade.delete()
        count_graded_assignment(assignment)
    cls_grade = ClassGrade.objects.filter(user_id=user_id, class_id=class_)
    cls_grade.delete()
    


# @receiver(post_delete, sender=Question)
# def question_deleted(sender, **kwargs):
#     question = kwargs['instance']
#     assignment = question.assignment_id
#     if(assignment):
#         count_graded_assignment(assignment)
#         students = assignment.class_id.students.all()
#         for student in students:
#             calculate_assignment_grades(assignment, student)
#             # calculate_class_grades(assignment.class_id, student)

#         calculate_assignment_properties(assignment)

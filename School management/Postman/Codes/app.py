from flask import Flask
from Controller.user_controller import user_blueprint  # Import the blueprint
from Controller.student_controller import student_blueprint
from Controller.teacher_controller import teacher_blueprint
from Controller.subject_controller import subject_blueprint
from Controller.staff_controller import staff_blueprint
from Controller.class_controller import class_blueprint
from Controller.attendance_controller import attendance_blueprint
from Controller.exam_controller import exam_blueprint
from Controller.exam_results_controller import exam_results_blueprint
from Controller.timetable_controller import timetable_blueprint
from Controller.fees_controller import fees_blueprint
from Controller.salary_controller import salary_blueprint

app = Flask(__name__)
app.register_blueprint(user_blueprint)  # Register the blueprint
app.register_blueprint(student_blueprint)
app.register_blueprint(teacher_blueprint)
app.register_blueprint(subject_blueprint)
app.register_blueprint(staff_blueprint)
app.register_blueprint(class_blueprint)
app.register_blueprint(attendance_blueprint)
app.register_blueprint(exam_blueprint)
app.register_blueprint(exam_results_blueprint)
app.register_blueprint(timetable_blueprint)
app.register_blueprint(fees_blueprint)
app.register_blueprint(salary_blueprint)

if __name__ == '__main__':
    app.run(debug=True)

# 필요한 라이브러리 임포트
import tkinter as tk
import os
from tkinter import filedialog, messagebox
from PyPDF2 import PdfReader, PdfWriter

# 선택된 PDF 파일 경로를 저장하는 전역 변수
selected_file_path = None

def select_pdf():
    # PDF 파일 선택 함수
    global selected_file_path
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])  # PDF 파일 선택 다이얼로그 열기
    if file_path:
        pdf_file_label.config(text=file_path)  # 선택된 파일 경로 표시
        update_total_pages(file_path)          # 총 페이지 수 업데이트
        selected_file_path = file_path         # 전역 변수에 파일 경로 저장
        split_button.config(state='normal')    # 분할 버튼 활성화

def update_total_pages(file_path):
    try:
        with open(file_path, "rb") as file:
            reader = PdfReader(file)
            total_pages = len(reader.pages)
            total_pages_var.set(f"{total_pages} 페이지")  # 페이지 수 표시 형식 수정
            
            # 페이지 입력 필드 업데이트 호출
            update_page_inputs()  # 페이지 수가 변경될 때 입력 필드 업데이트
            
    except Exception as e:
        messagebox.showwarning("경고", f"파일을 열 수 없습니다: {e}")

def start_processing():
    # PDF 분할 처리를 시작하는 함수
    global selected_file_path
    if selected_file_path is None:
        messagebox.showwarning("경고", "PDF 파일을 선택하세요.")
        return

    try:
        num_files = int(num_files_var.get())           # 분할할 파일 수 가져오기
        pages_info = []                                # 페이지 정보를 저장할 리스트
        
        # 총 페이지 수에서 숫자만 추출
        total_pages_str = total_pages_var.get().split()[0]  # "774 페이지" -> "774"
        total_pages = int(total_pages_str)       # 총 페이지 수 가져오기

        for i in range(num_files):
            if i == 0:
                start_page = 1  # First file starts at page 1 (1-based)
            else:
                start_page_input = start_page_vars[i].get().strip()  # Get the input value and strip whitespace
                start_page = int(start_page_input) if start_page_input.isdigit() else 0  # Check for digit
            
            end_page_input = end_page_vars[i].get().strip()  # Get the input value and strip whitespace
            end_page = int(end_page_input) if end_page_input.isdigit() else 0  # Check for digit

            # Validation of page numbers
            if start_page < 1 or end_page > total_pages or start_page >= end_page:
                raise ValueError("유효한 페이지 번호를 입력하세요.")

            pages_info.append((start_page - 1, end_page))  # Store pages for PdfWriter, adjust for 0-based

        split_pdf(selected_file_path, pages_info)
        messagebox.showinfo("알림", "PDF 분할이 완료되었습니다.")
    except ValueError as ve:
        messagebox.showwarning("경고", str(ve))
    except Exception as e:
        messagebox.showwarning("경고", str(e))

def split_pdf(file_path, pages_info):
    # PDF 파일을 실제로 분할하는 함수
    reader = PdfReader(file_path)                      # PDF 파일 읽기
    base_filename = os.path.splitext(os.path.basename(file_path))[0]  # 파일 이름 추출
    output_dir = os.path.dirname(file_path)            # 출력 디렉토리 설정

    for index, (start, end) in enumerate(pages_info):
        writer = PdfWriter()                           # PDF 작성자 객체 생성
        for page in range(start, end):
            writer.add_page(reader.pages[page])        # 페이지 추가

        # 분할된 PDF 파일 저장
        output_filename = os.path.join(output_dir, f"{base_filename}_{index + 1:02d}.pdf")
        with open(output_filename, "wb") as output_file:
            writer.write(output_file)

def update_page_inputs(*args):
    # total_pages_var에서 숫자만 추출
    total_pages_str = total_pages_var.get().split()[0]  # "0 페이지" -> "0"
    
    # 입력값이 숫자가 아닌 경우 리턴
    if not num_files_var.get().isdigit():
        return

    num_files = int(num_files_var.get())
    total_pages = int(total_pages_str)
    
    # 이전 입력 필드 제거
    for widget in file_frame.winfo_children():
        widget.destroy()

    # 페이지 입력 변수 리스트 초기화
    start_page_vars.clear()
    end_page_vars.clear()

    # 새로운 입력 필드 생성
    for i in range(num_files):
        file_row = tk.Frame(file_frame)  # 각 파일별 프레임 생성
        file_row.pack(fill="x", pady=5)

        # 레이블을 왼쪽에 배치
        tk.Label(file_row, text=f"{i + 1}번째 파일:", font=("Arial", 10), width=15).pack(side="left")

        start_page_var = tk.StringVar(value="1" if i == 0 else "")
        end_page_var = tk.StringVar()
        start_page_vars.append(start_page_var)
        end_page_vars.append(end_page_var)

        # 입력 필드들을 같은 줄에 배치
        start_entry = tk.Entry(file_row, textvariable=start_page_var, width=10, justify='center',
                             state='readonly' if i == 0 else 'normal')
        start_entry.pack(side="left", padx=(5, 5))
        
        tk.Label(file_row, text="~", font=("Arial", 10)).pack(side="left", padx=(0, 5))

        end_entry = tk.Entry(file_row, textvariable=end_page_var, width=10, justify='center')
        end_entry.pack(side="left", padx=(0, 5))
        tk.Label(file_row, text="페이지", font=("Arial", 10)).pack(side="left")

        if i == 1:
            global end_page_var_2
            end_page_var_2 = end_page_var

    # 자동으로 페이지 번호 설정
    if total_pages > 0:
        # 첫 번째 파일의 시작 페이지는 항상 1
        start_page_vars[0].set("1")
        
        # 마지막 파일의 끝 페이지는 총 페이지 수로 설정
        if end_page_vars:
            end_page_vars[-1].set(str(total_pages))
            
        # 중간 파일들의 페이지는 비워둠
        for j in range(num_files - 1):
            if j > 0:  # 첫 번째 파일 제외
                start_page_vars[j].set("")
            if j < num_files - 1:  # 마지막 파일 제외
                end_page_vars[j].set("")

    adjust_window_size(num_files)

def adjust_window_size(num_files):
    # 최소 창 크기 설정
    base_height = 345
    additional_height_per_file = 40
    min_height = base_height + num_files * additional_height_per_file
    
    # 최소 창 크기 설정
    root.minsize(600, min_height)
    
    # 현재 창 크기가 최소 크기보다 작다면 조정
    current_width = root.winfo_width()
    current_height = root.winfo_height()
    if current_height < min_height:
        root.geometry(f"{current_width}x{min_height}")

# GUI 메인 윈도우 생성
root = tk.Tk()
root.title("PDF 파일 분할기(muttul_Var_2025_0105_0138)")
root.geometry("500x600")  # 초기 창 크기 조정
root.resizable(False, True)  # 가로 크기 고정, 세로 크기만 조절 가능

# 메인 프레임 생성
main_frame = tk.Frame(root, padx=20, pady=20)
main_frame.pack(fill=tk.BOTH, expand=True)

# 제목 레이블
title_label = tk.Label(main_frame, text="PDF 파일 분할기", font=("Arial", 16, "bold"))
title_label.pack(pady=(0, 20))

# 파일 선택 섹션
file_section = tk.Frame(main_frame)
file_section.pack(fill=tk.X, pady=(0, 10))

select_button = tk.Button(file_section, text="PDF 파일 선택", command=select_pdf, width=15)
select_button.pack(pady=(0, 5))

pdf_file_label = tk.Label(file_section, text="선택된 파일 없음", fg="gray", wraplength=400)
pdf_file_label.pack()

# 정보 표시 섹션
info_frame = tk.Frame(main_frame)
info_frame.pack(fill=tk.X, pady=10)

# 총 페이지 수 표시
page_info = tk.Frame(info_frame)
page_info.pack(fill=tk.X, pady=5)
tk.Label(page_info, text="총 페이지 수:", font=("Arial", 10)).pack(side=tk.LEFT)
total_pages_var = tk.StringVar(value="0 페이지")
tk.Label(page_info, textvariable=total_pages_var, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)

# 파일 개수 설정
count_frame = tk.Frame(info_frame)
count_frame.pack(fill=tk.X, pady=5)
tk.Label(count_frame, text="분할할 파일 개수:", font=("Arial", 10)).pack(side=tk.LEFT)
num_files_var = tk.StringVar(value="2")
num_files_var.trace_add('write', update_page_inputs)
num_files_entry = tk.Spinbox(count_frame, from_=1, to=10, textvariable=num_files_var, 
                            width=5, justify='center', state='readonly')
num_files_entry.pack(side=tk.LEFT, padx=5)

# 페이지 입력 프레임
file_frame = tk.LabelFrame(main_frame, text=" 페이지 범위 설정 ", font=("Arial", 10))
file_frame.pack(fill=tk.BOTH, expand=True, pady=10)

# 버튼 프레임
button_frame = tk.Frame(main_frame)
button_frame.pack(pady=10)

split_button = tk.Button(button_frame, text="분할 시작", command=start_processing, 
                        width=12, state='disabled')
split_button.pack(side=tk.LEFT, padx=5)

tk.Button(button_frame, text="프로그램 종료", command=root.destroy, 
          width=12).pack(side=tk.LEFT, padx=5)

# 전역 변수 초기화
start_page_vars = []
end_page_vars = []

# 초기 페이지 입력 필드 생성
update_page_inputs()

root.mainloop()
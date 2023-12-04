import streamlit as st
import pandas as pd
import os
import streamlit_calendar as st_calendar
import uuid

st.set_page_config(layout='wide')

# カレンダーの設定
# オプションを指定
calendar_options = {
    'initialView': 'dayGridMonth',
    'headerToolbar': {
        'left': 'today prev,next',
        'center': 'title',
        'right': '',
        # 'right': 'dayGridMonth,timeGridWeek',
    },
    'footerToolbar': {
    },
    'titleFormat': {
        'year': 'numeric', 'month': '2-digit', 'day': '2-digit'
    },
    'buttonText': {
    },
    'locale': 'ja', # 日本語化する
    'firstDay': '0', 
    # 'resourceEditable': 'true',
    # 'editable': 'true',
}

# タスク管理用のcsvファイルを作成
if os.path.exists('tasks.csv'):
    tasks = pd.read_csv('tasks.csv')
else:
    tasks = pd.DataFrame(columns=['id', 'Task', 'Deadline', 'Priority', 'Category'])
    tasks.to_csv('tasks.csv', index=False)

# カテゴリの一覧
categories = tasks['Category'].unique().tolist()

# タスクの追加
def add_task(task, deadline, priority, category):
    global tasks
    id = str(uuid.uuid4())
    new_task = pd.DataFrame({'id':[id], 'Task': [task], 'Deadline': [deadline], 'Priority': [priority], 'Category': [category]})
    tasks = pd.concat([tasks, new_task])
    tasks.reset_index(inplace=True, drop=True)
    tasks.to_csv('tasks.csv', index=False)

# タスクの編集
def edit_task(index, task, deadline, priority, category):
    global tasks
    tasks.at[index, 'Task'] = task
    tasks.at[index, 'Deadline'] = deadline
    tasks.at[index, 'Priority'] = priority
    tasks.at[index, 'Category'] = category
    tasks.to_csv('tasks.csv', index=False)

# タスクの削除
def delete_task(index):
    global tasks
    tasks = tasks.drop(index)
    tasks.reset_index(inplace=True, drop=True)
    tasks.to_csv('tasks.csv', index=False)

# タスクを表示し、ソートする
def display_tasks(sort_by=None, filter_by=None):
    global tasks
    _tasks = tasks
    if sort_by:
        _tasks = tasks.sort_values(by=sort_by)
    if filter_by:
        _tasks = tasks[tasks['Category'] == filter_by]
    tab1, tab2 = st.tabs(['Calendar veiw', 'List veiw'])
    with tab2: # List veiw
        st.table(_tasks[['Task', 'Deadline', 'Priority', 'Category']])
    with tab1: # Calendar veiw
        st_calendar.calendar(events=_tasks.rename(columns={'Task':'title', 'Deadline':'start'}).to_dict('records'), options=calendar_options)

# Streamlitアプリの本体
def main():
    st.title("タスク管理アプリ")

    # タスクの表示とソートとフィルタリング
    st.header("タスクリスト")


    if not tasks.empty:
        sort_by = st.selectbox("ソート:", ['None', 'Task', 'Deadline', 'Priority'])
        filter_by = st.selectbox("フィルター:", ['None'] + categories)
        sort_by = None if sort_by == 'None' else sort_by
        filter_by = None if filter_by == 'None' else filter_by
        display_tasks(sort_by, filter_by)
        
    else:
        st.warning("タスクがありません。新しいタスクを追加してください。")

    with st.expander("タスクの追加", expanded=False):
        task_name = st.text_input("タスク名:")
        deadline = st.date_input("期限:")
        priority = st.selectbox("優先順位:", ['低', '中', '高'], key='priority')
        category = st.selectbox("カテゴリ:", categories + ['カテゴリを追加'], key='category')
        if category == 'カテゴリを追加':
            new_category = st.text_input("新しいカテゴリ名:")
            category = new_category.strip()  # 空白を削除
            categories.append(category)
            if not category:
                st.warning("カテゴリ名を入力してください。")

        if st.button("追加"):
            if not task_name:
                st.warning("タスク名を入力してください。")
            elif task_name in tasks['Task'].values:
                st.warning("同じタスク名が既に存在します。")
            else:
                add_task(task_name, deadline, priority, category)
                
    # タスクの編集
    if not tasks.empty:
        with st.expander("タスクの編集", expanded=False):
            selected_task_index = st.selectbox("編集するタスクを選択:", tasks.index, format_func=lambda x: tasks.at[x, 'Task'])
            edited_task_name = st.text_input("タスク名:", value=tasks.at[selected_task_index, 'Task'])
            edited_deadline = st.date_input("期限:", value=pd.to_datetime(tasks.at[selected_task_index, 'Deadline']))
            edited_priority = st.selectbox("優先順位:", ['低', '中', '高'], index=['低', '中', '高'].index(tasks.at[selected_task_index, 'Priority']))
            edited_category = st.selectbox("カテゴリ:", categories + ['カテゴリを追加'], key='edit_category')
            if edited_category == 'カテゴリを追加':
                new_category = st.text_input("新しいカテゴリ名:", value=tasks.at[selected_task_index, 'Category'])
                edited_category = new_category.strip()  # 空白を削除
                if not edited_category:
                    st.warning("カテゴリ名を入力してください。")

            if st.button("更新"):
                if edited_task_name in tasks['Task'].values and edited_task_name != tasks.at[selected_task_index, 'Task']:
                    st.warning("同じタスク名が既に存在します。")
                else:
                    edit_task(selected_task_index, edited_task_name, edited_deadline, edited_priority, edited_category)

    # タスクの削除
    if not tasks.empty:
        with st.expander("タスクの削除", expanded=False):
            deleted_task_index = st.selectbox("削除するタスクを選択:", tasks.index, format_func=lambda x: tasks.at[x, 'Task'])
            if st.button("削除"):
                delete_task(deleted_task_index)



if __name__ == "__main__":
    main()

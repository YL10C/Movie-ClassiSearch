import mysql.connector

def create_fulltext_indexes():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Cyl200124@',
            database='movie_search'
        )
        cursor = conn.cursor()

        # 为movies表的title和plot列添加全文索引
        try:
            cursor.execute("""
                ALTER TABLE movies 
                ADD FULLTEXT INDEX idx_title_plot (title, plot)
            """)
            print("成功创建movies表的全文索引")
        except mysql.connector.Error as err:
            if err.errno == 1061:  # 索引已存在的错误码
                print("movies表的全文索引已存在")
            else:
                print(f"创建movies表索引时出错: {err}")

        # 为actors表的name列添加全文索引
        try:
            cursor.execute("""
                ALTER TABLE actors 
                ADD FULLTEXT INDEX idx_actor_name (name)
            """)
            print("成功创建actors表的全文索引")
        except mysql.connector.Error as err:
            if err.errno == 1061:
                print("actors表的全文索引已存在")
            else:
                print(f"创建actors表索引时出错: {err}")

        conn.commit()
        print("所有索引创建完成")

    except mysql.connector.Error as err:
        print(f"数据库连接错误: {err}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        print("数据库连接已关闭")

if __name__ == "__main__":
    create_fulltext_indexes() 
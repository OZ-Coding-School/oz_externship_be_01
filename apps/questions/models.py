"""
Table question_categories {
  id bigint [primary key, not null]
  parent_id bigint [not null]
  name varchar(15) [not null]
  created_at datetime
  updated_at datetime
}
Ref: question_categories.parent_id > question_categories.id
Ref: questions.category_id > question_categories.id
"""

"""
Table questions {
  id bigint [primary key, not null]
  category_id bigint [not null]
  author_id bigint
  title varchar(50) [not null]
  content text [not null]
  view_count bigint [not null, default: 0]
  created_at datetime
  updated_at datetime
}
Ref: questions.author_id > user.id
"""

"""
Table question_ai_answers {
  id bigint [primary key, not null]
  question_id bigint [not null]
  content text [not null]
  created_at datetime
  updated_at datetime
}
Ref: question_ai_answers.question_id - questions.id
"""

"""
Table question_images {
  id bigint [primary key, not null]
  question_id bigint [not null]
  img_url varchar(255) [not null]
  created_at datetime
  updated_at datetime
}
Ref: question_images.question_id > questions.id
"""

"""
Table answers {
  id bigint [primary key, not null]
  question_id bigint [not null]
  author_id bigint [not null]
  content text [not null]
  is_adopted boolean [default: false]
  created_at datetime
  updated_at datetime
}
Ref: answers.question_id > questions.id
Ref: answers.author_id > user.id
"""

"""
Table answer_images {
  id bigint [primary key, not null]
  answer_id bigint [not null]
  img_url varchar(255) [not null]
  created_at datetime
  updated_at datetime
}
Ref: answer_images.answer_id > answers.id
"""

"""
Table answer_comments {
  id bigint [primary key, not null]
  answer_id bigint [not null]
  author_id bigint [not null]
  content text [not null]
  created_at datetime
  updated_at datetime
}
Ref: answer_comments.author_id > user.id
Ref: answer_comments.answer_id > answers.id
"""
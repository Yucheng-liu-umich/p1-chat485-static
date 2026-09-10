# README for EECS 485 p1 static webpage
> this readme works as notebook for/during project progress

1. environment and tools setup completed. move to page 6 `hand-coded HTML`
2. hondcode part partially done: 9.3

# submission questions
1. what do we wo with the handcode html; is css must, how ot submit 

# 2. check be fore submission
ruff check chat485generator tests/test_student.py
ruff format --check chat485generator tests/test_student.py
pytest -v
bin/chat485test
git status

# 3. submisssion tar command

rm -f submit.tar.gz

tar \
  --disable-copyfile \
  --exclude '*__pycache__*' \
  --exclude 'chat485_html' \
  --exclude 'generated_html' \
  -czvf submit.tar.gz \
  bin \
  handcoded_html \
  chat485 \
  chat485generator \
  tests/test_student.py

# 4. check tar (no unwanted directories)

tar -tzf submit.tar.gz

# no oversize

du -h submit.tar.gz

# and you can upload now

# what we learn here
1. `div` tag
```html
    <div class="main">
        <p>Select a conversation or new chat</p>
    </div>
```

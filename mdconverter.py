import re
import os
import sys
from datetime import datetime
from shutil import copyfile

def get_time(ms=datetime.utcnow().timestamp(), fmt='%Y-%m-%d %H:%M:%S.%f'):
    date = datetime.fromtimestamp(ms)
    iso = date.strftime(fmt)
    return iso[:-3] + 'Z'

def build_pair(key, value):
    final_val = ""
    if not isinstance(value, list):
        final_val = value
    else:
        final_val = "\n"
        for item in value:
            final_val += "  - {}\n".format(item)
    return "{}: {}".format(key, final_val)

date_filename_re = re.compile('([0-9]{4}-[0-9]{2}-[0-9]{2}[-_])')
casing_re = re.compile('(^|\s)([a-z])(\w+)')
def add_meta(filename, tags, comments=True, published=True):
    with open(filename) as f:
        contents = f.read()
    lines = contents.split("\n")
    first_line = lines[0]
    if first_line.startswith("---"):
        print("Metadata already present! Skipping!")
        return None
    title = None
    line_offset = 0
    
    if date_filename_re.match(filename):
         created_date = date_filename_re.findall(filename)[0][:-1]
         created_date += get_time(fmt=" %H:%M:%S.%f")
    else:
        created_date = get_time()
    # Nab a title if it's there.
    if first_line.startswith("#"):
        # Skip the pound!
        title = first_line[1:].strip()
        line_offset = len(first_line)
    else:
        # 2019-05-06-example-post
        if date_filename_re.match(filename):
            title = filename.split(".")[0]
            # Becomes 'example-post'
            title = date_filename_re.sub("", title)
            # Becomes 'example post'
            title = re.sub(title, "[-_]", "")
            # Becomes 'Example Post'
            title = casing_re.sub(lambda pattern: pattern.group(1) + pattern.group(2).upper() + pattern.group(3), title)

    excerpt = contents[line_offset:].strip().split(".")[0] + "..."
    excerpt = excerpt.split("\n")[0][:80]
    meta = build_pair("layout", "post")
    if title:
        meta += "\n" + build_pair("title", title)
    meta += "\n" + build_pair("date", created_date)
    meta += "\n" + build_pair("excerpt", excerpt)
    meta += "\n" + build_pair("tags", tags)
    meta += "\n" + build_pair("comments", str(comments).lower())
    meta += "\n" + build_pair("published", str(published).lower())
    return "---\n{}\n---\n{}".format(meta, contents[line_offset:])
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: {} <filename> [tagA,tagB] [published: true/false] [comments: true/false]".format(sys.argv[0]))
        sys.exit(0)
    published = True
    comments = True
    tags = []
    print(sys.argv)
    if len(sys.argv) >= 3:
        tags = sys.argv[2].split(",")
    if len(sys.argv) >= 4:
        published = sys.argv[3].lower() == "true"
    if len(sys.argv) >= 5:
        comments = sys.argv[4].lower() == "true"
    
    filename = sys.argv[1]
    result = add_meta(filename, tags, published, comments)
    if not result:
        sys.exit(-1)
    bckup = filename + '.bck'
    idx = 0
    while os.path.isfile(bckup):
        idx += 1
        bckup = filename + '.' + str(idx) + '.bck'
    copyfile(filename, bckup)
    with open(filename, 'w') as f:
        f.write(result)
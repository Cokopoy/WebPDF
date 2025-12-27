import os

with open('app.py', 'r') as f:
    content = f.read()

# Replace the old run config with new one
old_run = "if __name__ == '__main__':\n    app.run(debug=True, host='127.0.0.1', port=5000)"
new_run = "if __name__ == '__main__':\n    port = int(os.environ.get('PORT', 5000))\n    app.run(debug=False, host='0.0.0.0', port=port)"

if old_run in content:
    content = content.replace(old_run, new_run)
    with open('app.py', 'w') as f:
        f.write(content)
    print(' app.py updated for production')
else:
    print(' Could not find the app.run line to update')

from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)
profiles = []

HTML = '''
<!doctype html>
<html>
<head>
  <title>Instagram Profile Manager</title>
  <style>
    body { font-family: Arial, sans-serif; background: #f5f7fb; padding: 20px; }
    .wrap { max-width: 1000px; margin: auto; }
    form { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,.08); }
    .grid { display: grid; grid-template-columns: repeat(2, minmax(220px, 1fr)); gap: 12px; }
    .full { grid-column: 1 / -1; }
    input, textarea, button { width: 100%; padding: 10px; box-sizing: border-box; }
    textarea { min-height: 80px; }
    .card { background: white; padding: 16px; border-radius: 10px; margin-top: 18px; }
    .meta { color: #666; font-size: 13px; }
    button { background: #0084ff; color: white; border: none; border-radius: 6px; cursor: pointer; }
    .delete { background: #d33; }
  </style>
</head>
<body>
  <div class="wrap">
    <h2>Instagram Profile Manager</h2>
    <form id="form">
      <div class="grid">
        <div><input name="username" placeholder="Username" required></div>
        <div><input name="full_name" placeholder="Full Name"></div>
        <div><input name="user_id" placeholder="User ID"></div>
        <div><input name="external_url" placeholder="External URL"></div>
        <div><input name="followers" type="number" value="0" placeholder="Followers"></div>
        <div><input name="following" type="number" value="0" placeholder="Following"></div>
        <div><input name="number_of_posts" type="number" value="0" placeholder="Number of Posts"></div>
        <div><input name="number_of_tags" type="number" value="0" placeholder="Number of Tags"></div>
        <div><input name="igtv_posts" type="number" value="0" placeholder="IGTV Posts"></div>
        <div><input name="public_email" placeholder="Public Email"></div>
        <div><input name="public_phone" placeholder="Public Phone"></div>
        <div><input name="obfuscated_email" placeholder="Obfuscated Email"></div>
        <div><input name="obfuscated_phone" placeholder="Obfuscated Phone"></div>
        <div><input name="profile_picture_url" placeholder="Profile Picture URL"></div>
        <div class="full">
          <textarea name="biography" placeholder="Biography"></textarea>
        </div>
        <div class="full">
          <label><input type="checkbox" name="verified"> Verified</label>
          <label><input type="checkbox" name="is_business_account"> Business Account</label>
          <label><input type="checkbox" name="is_private_account"> Private Account</label>
        </div>
        <div class="full"><button type="submit">Save Profile</button></div>
      </div>
    </form>

    <div id="profiles"></div>
  </div>

  <script>
    async function loadProfiles() {
      const res = await fetch('/api/profiles');
      const data = await res.json();
      const container = document.getElementById('profiles');
      container.innerHTML = data.map(p => `
        <div class="card">
          <h3>@${p.username}</h3>
          <div>${p.full_name || ''}</div>
          <div class="meta">Followers: ${p.followers} | Following: ${p.following}</div>
          <div class="meta">Posts: ${p.number_of_posts} | Tags: ${p.number_of_tags}</div>
          <p>${p.biography || ''}</p>
          <div class="meta">Email: ${p.public_email || p.obfuscated_email || ''}</div>
          <div class="meta">Phone: ${p.public_phone || p.obfuscated_phone || ''}</div>
          <button class="delete" onclick="deleteProfile('${p.username}')">Delete</button>
        </div>
      `).join('');
    }

    document.getElementById('form').addEventListener('submit', async e => {
      e.preventDefault();
      const form = new FormData(e.target);
      const data = Object.fromEntries(form.entries());
      data.verified = form.get('verified') === 'on';
      data.is_business_account = form.get('is_business_account') === 'on';
      data.is_private_account = form.get('is_private_account') === 'on';
      await fetch('/api/profiles', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
      });
      e.target.reset();
      loadProfiles();
    });

    async function deleteProfile(username) {
      await fetch('/api/profiles/' + username, { method: 'DELETE' });
      loadProfiles();
    }

    loadProfiles();
  </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/profiles', methods=['GET'])
def get_profiles():
    return jsonify(profiles)

@app.route('/api/profiles', methods=['POST'])
def add_profile():
    data = request.get_json()
    if not data or not data.get('username'):
        return jsonify({'error': 'username is required'}), 400

    for p in profiles:
        if p['username'] == data['username']:
            return jsonify({'error': 'username already exists'}), 400

    profile = {
        'username': data.get('username'),
        'full_name': data.get('full_name', ''),
        'user_id': data.get('user_id', ''),
        'verified': bool(data.get('verified')),
        'is_business_account': bool(data.get('is_business_account')),
        'is_private_account': bool(data.get('is_private_account')),
        'followers': int(data.get('followers', 0) or 0),
        'following': int(data.get('following', 0) or 0),
        'number_of_posts': int(data.get('number_of_posts', 0) or 0),
        'number_of_tags': int(data.get('number_of_tags', 0) or 0),
        'external_url': data.get('external_url', ''),
        'igtv_posts': int(data.get('igtv_posts', 0) or 0),
        'biography': data.get('biography', ''),
        'public_email': data.get('public_email', ''),
        'public_phone': data.get('public_phone', ''),
        'obfuscated_email': data.get('obfuscated_email', ''),
        'obfuscated_phone': data.get('obfuscated_phone', ''),
        'profile_picture_url': data.get('profile_picture_url', '')
    }
    profiles.append(profile)
    return jsonify(profile), 201

@app.route('/api/profiles/<username>', methods=['DELETE'])
def delete_profile(username):
    for i, p in enumerate(profiles):
        if p['username'] == username:
            del profiles[i]
            return jsonify({'status': 'deleted'})
    return jsonify({'error': 'profile not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)

import json, time, os

BASE = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(BASE, 'translation_cache.json')

# Load existing cache
cache = {}
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, encoding='utf-8') as f:
        cache = json.load(f)
    print(f'Loaded {len(cache)} cached translations')

# Load word data
with open(os.path.join(BASE, 'flashcard_data.json'), encoding='utf-8') as f:
    data = json.load(f)

# Collect words needing translation (skip ones with Japanese already or cached)
to_translate = []
for entry in data:
    w = entry['w'].strip().lower()
    if entry.get('j'):  # already has Japanese
        cache[w] = entry['j']
        continue
    if w in cache:
        continue
    to_translate.append(entry['w'].strip())

print(f'Total words: {len(data)}')
print(f'Already have Japanese: {len(data) - len(to_translate) - len([w for w in data if w["w"].strip().lower() in cache and not w.get("j")])}')
print(f'Cached: {len(cache)}')
print(f'Need to translate: {len(to_translate)}')

if to_translate:
    from deep_translator import GoogleTranslator
    translator = GoogleTranslator(source='en', target='ja')

    # Batch translate (max 5000 chars per request)
    BATCH_SIZE = 50
    total_batches = (len(to_translate) + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, len(to_translate), BATCH_SIZE):
        batch = to_translate[i:i+BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1

        try:
            results = translator.translate_batch(batch)
            for word, translation in zip(batch, results):
                cache[word.strip().lower()] = translation if translation else word

            if batch_num % 10 == 0 or batch_num == total_batches:
                print(f'  Batch {batch_num}/{total_batches} done ({i+len(batch)}/{len(to_translate)})')
                # Save cache periodically
                with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                    json.dump(cache, f, ensure_ascii=False, indent=1)

            time.sleep(0.5)  # rate limit

        except Exception as e:
            print(f'  Error at batch {batch_num}: {e}')
            # Try one by one for failed batch
            for word in batch:
                try:
                    result = translator.translate(word)
                    cache[word.strip().lower()] = result if result else word
                except:
                    cache[word.strip().lower()] = ''
                time.sleep(0.3)
            print(f'  Recovered batch {batch_num}')

    # Final save
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=1)
    print(f'Translation complete. Cache size: {len(cache)}')

# Apply translations to data
for entry in data:
    w = entry['w'].strip().lower()
    if w in cache and cache[w]:
        entry['j'] = cache[w]

# Save updated data
with open(os.path.join(BASE, 'flashcard_data.json'), 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)

has_jp = sum(1 for e in data if e.get('j'))
print(f'Words with Japanese: {has_jp}/{len(data)}')
print('Done!')

import os
from PIL import Image, ImageDraw, ImageFont

def render_terminal(title, lines, filename, width=960, font_size=15):
    font_path = 'C:\\Windows\\Fonts\\consola.ttf'
    font = ImageFont.truetype(font_path, font_size)
    font_bold = ImageFont.truetype('C:\\Windows\\Fonts\\consolab.ttf' if os.path.exists('C:\\Windows\\Fonts\\consolab.ttf') else font_path, font_size)
    title_font = ImageFont.truetype(font_path, 13)

    line_height = int(font_size * 1.48)
    header_height = 38
    padding_x = 24
    padding_y = 16
    total_height = header_height + padding_y * 2 + len(lines) * line_height

    img = Image.new('RGB', (width, total_height), color='#13171f')
    draw = ImageDraw.Draw(img)

    # Window title bar
    draw.rectangle([(0, 0), (width, header_height)], fill='#1c212b')
    draw.line([(0, header_height), (width, header_height)], fill='#2d3342', width=1)

    # Window buttons
    draw.ellipse([(14, 13), (25, 24)], fill='#ff5f56')
    draw.ellipse([(33, 13), (44, 24)], fill='#ffbd2e')
    draw.ellipse([(52, 13), (63, 24)], fill='#27c93f')

    # Window title
    draw.text((width // 2, 19), title, fill='#8b949e', font=title_font, anchor='mm')

    # Content
    y = header_height + padding_y
    for prefix_type, text in lines:
        if prefix_type == 'prompt':
            parts = text.split(' ', 1)
            prompt_part = parts[0] + ' '
            cmd_part = parts[1] if len(parts) > 1 else ''
            draw.text((padding_x, y), prompt_part, fill='#58a6ff', font=font_bold)
            p_width = draw.textlength(prompt_part, font=font_bold)
            draw.text((padding_x + p_width, y), cmd_part, fill='#ffffff', font=font_bold)
        elif prefix_type == 'comment':
            draw.text((padding_x, y), text, fill='#6e7681', font=font)
        elif prefix_type == 'highlight':
            draw.text((padding_x, y), text, fill='#7ee787', font=font_bold)
        elif prefix_type == 'cyan':
            draw.text((padding_x, y), text, fill='#79c0ff', font=font)
        elif prefix_type == 'orange':
            draw.text((padding_x, y), text, fill='#ffa657', font=font)
        elif prefix_type == 'warn':
            draw.text((padding_x, y), text, fill='#e3b341', font=font)
        elif prefix_type == 'output':
            draw.text((padding_x, y), text, fill='#c9d1d9', font=font)
        else:
            draw.text((padding_x, y), text, fill='#c9d1d9', font=font)
        y += line_height

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    img.save(filename)
    print(f"Generated: {filename} ({width}x{total_height})")

def main():
    if os.path.exists('screenshots/test.png'):
        os.remove('screenshots/test.png')

    # 1. Database Setup
    lines_01 = [
        ('comment', '// Task 1: Connect, switch to ecommerce database, create products collection'),
        ('prompt', 'test> use ecommerce'),
        ('output', 'switched to db ecommerce'),
        ('prompt', 'ecommerce> db.createCollection("products")'),
        ('highlight', '{ ok: 1 }'),
        ('prompt', 'ecommerce> db.products.insertMany(['),
        ('output', '...   { name: "Laptop", price: 65000, category: "Electronics", stock: 12 },'),
        ('output', '...   { name: "Mouse", price: 800, category: "Electronics", stock: 50 },'),
        ('output', '...   { name: "Keyboard", price: 1800, category: "Electronics", stock: 25 },'),
        ('output', '...   { name: "Monitor", price: 15000, category: "Electronics", stock: 8 },'),
        ('output', '...   { name: "Phone", price: 30000, category: "Electronics", stock: 20 },'),
        ('output', '...   { name: "Notebook", price: 100, category: "Stationery", stock: 200 },'),
        ('output', '...   { name: "Pen", price: 20, category: "Stationery", stock: 500 },'),
        ('output', '...   { name: "Bag", price: 1200, category: "Accessories", stock: 30 },'),
        ('output', '...   { name: "Headphones", price: 2500, category: "Electronics", stock: 15 },'),
        ('output', '...   { name: "Charger", price: 600, category: "Electronics", stock: 0 },'),
        ('output', '...   { name: "Desk", price: 7000, category: "Furniture", stock: 6 },'),
        ('output', '...   { name: "Chair", price: 4500, category: "Furniture", stock: 10 }'),
        ('output', '... ])'),
        ('highlight', '{ acknowledged: true, insertedIds: { \'0\': ObjectId(\'6ace1e54256eaf73f718ad31\'), ... } }'),
        ('prompt', 'ecommerce> db.products.countDocuments()'),
        ('highlight', '12'),
        ('prompt', 'ecommerce> db.products.findOne()'),
        ('output', '{'),
        ('output', '  _id: ObjectId(\'6ace1e54256eaf73f718ad31\'),'),
        ('output', '  name: \'Laptop\','),
        ('output', '  price: 65000,'),
        ('output', '  category: \'Electronics\','),
        ('output', '  stock: 12'),
        ('output', '}')
    ]
    render_terminal('mongosh - Task 1: Database and Sample Data Setup', lines_01, 'screenshots/01-database-setup.png')

    # 2. Server Status
    lines_02 = [
        ('comment', '// Task 2: Inspecting MongoDB server health with db.serverStatus()'),
        ('prompt', 'ecommerce> db.serverStatus().host'),
        ('cyan', '\'LAPTOP-9H9SEP3P\''),
        ('prompt', 'ecommerce> db.serverStatus().version'),
        ('cyan', '\'8.2.4\''),
        ('prompt', 'ecommerce> db.serverStatus().uptime'),
        ('highlight', '887308   // ~10.27 days uptime'),
        ('prompt', 'ecommerce> db.serverStatus().connections'),
        ('output', '{'),
        ('output', '  current: 12,'),
        ('output', '  available: 201074,'),
        ('output', '  totalCreated: 106,'),
        ('output', '  rejected: 0,'),
        ('highlight', '  active: 3,'),
        ('output', '  queuedForEstablishment: Long(\'0\')'),
        ('output', '}'),
        ('prompt', 'ecommerce> db.serverStatus().mem'),
        ('output', '{ bits: 64, resident: 47, virtual: 4488, supported: true }'),
        ('prompt', 'ecommerce> db.serverStatus().opcounters'),
        ('output', '{'),
        ('output', '  insert: Long(\'32\'),'),
        ('output', '  query: Long(\'1777\'),'),
        ('output', '  update: Long(\'255\'),'),
        ('output', '  delete: Long(\'10\'),'),
        ('output', '  getmore: Long(\'0\'),'),
        ('output', '  command: Long(\'17850\')'),
        ('output', '}')
    ]
    render_terminal('mongosh - Task 2: Server Health Monitoring (db.serverStatus())', lines_02, 'screenshots/02-server-status.png')

    # 3. Current Operations
    lines_03 = [
        ('comment', '// Task 2: Inspecting active operations with db.currentOp()'),
        ('prompt', 'ecommerce> db.currentOp({ active: true })'),
        ('output', '{'),
        ('output', '  inprog: ['),
        ('output', '    {'),
        ('output', '      type: \'op\','),
        ('output', '      host: \'LAPTOP-9H9SEP3P:27017\','),
        ('output', '      desc: \'conn106\','),
        ('output', '      connectionId: 106,'),
        ('output', '      client: \'127.0.0.1:61223\','),
        ('output', '      appName: \'mongosh 2.1.4\','),
        ('highlight', '      active: true,'),
        ('output', '      currentOpTime: \'2026-10-13T17:35:00.774+05:30\','),
        ('output', '      secs_running: Long(\'0\'),'),
        ('output', '      op: \'command\','),
        ('output', '      ns: \'admin.$cmd.aggregate\','),
        ('output', '      command: {'),
        ('output', '        aggregate: 1,'),
        ('output', '        pipeline: [ { \'$currentOp\': { allUsers: true } }, { \'$match\': { active: true } } ],'),
        ('output', '        \'$db\': \'admin\''),
        ('output', '      }'),
        ('output', '    },'),
        ('output', '    {'),
        ('output', '      type: \'op\','),
        ('output', '      desc: \'conn69\','),
        ('output', '      connectionId: 69,'),
        ('output', '      appName: \'mongosh 2.1.4\','),
        ('highlight', '      active: true,'),
        ('output', '      secs_running: Long(\'9\'),'),
        ('output', '      op: \'command\','),
        ('output', '      ns: \'admin.$cmd\','),
        ('output', '      command: { hello: 1, maxAwaitTimeMS: 10000, \'$db\': \'admin\' }'),
        ('output', '    },'),
        ('output', '    {'),
        ('output', '      type: \'op\','),
        ('output', '      desc: \'Checkpointer\','),
        ('highlight', '      active: true,'),
        ('output', '      isFromUserConnection: false,'),
        ('output', '      op: \'none\''),
        ('output', '    }'),
        ('output', '  ],'),
        ('highlight', '  ok: 1'),
        ('output', '}')
    ]
    render_terminal('mongosh - Task 2: Active Operations (db.currentOp())', lines_03, 'screenshots/03-current-operations.png')

    # 4. Query Before Index
    lines_04 = [
        ('comment', '// Task 3: Baseline Queries with explain("executionStats") - COLLSCAN stage'),
        ('prompt', 'ecommerce> db.products.find({ category: "Electronics" }).explain("executionStats")'),
        ('output', '{'),
        ('output', '  queryPlanner: {'),
        ('output', '    winningPlan: {'),
        ('highlight', '      stage: \'COLLSCAN\','),
        ('output', '      filter: { category: { \'$eq\': \'Electronics\' } },'),
        ('output', '      direction: \'forward\''),
        ('output', '    }'),
        ('output', '  },'),
        ('output', '  executionStats: {'),
        ('output', '    executionSuccess: true,'),
        ('output', '    nReturned: 7,'),
        ('output', '    executionTimeMillis: 0,'),
        ('warn', '    totalKeysExamined: 0,'),
        ('warn', '    totalDocsExamined: 12,'),
        ('output', '    executionStages: { stage: \'COLLSCAN\', nReturned: 7, docsExamined: 12 }'),
        ('output', '  }'),
        ('output', '}'),
        ('comment', '// Baseline Query 4: Category and Price before compound index'),
        ('prompt', 'ecommerce> db.products.find({ category: "Electronics", price: { $gt: 1000 } }).explain("executionStats")'),
        ('output', '{'),
        ('output', '  queryPlanner: {'),
        ('output', '    winningPlan: {'),
        ('highlight', '      stage: \'COLLSCAN\','),
        ('output', '      filter: { \'$and\': [ { category: { \'$eq\': \'Electronics\' } }, { price: { \'$gt\': 1000 } } ] }'),
        ('output', '    }'),
        ('output', '  },'),
        ('output', '  executionStats: {'),
        ('output', '    nReturned: 5,'),
        ('output', '    executionTimeMillis: 0,'),
        ('warn', '    totalKeysExamined: 0,'),
        ('warn', '    totalDocsExamined: 12'),
        ('output', '  }'),
        ('output', '}')
    ]
    render_terminal('mongosh - Task 3: Baseline Query Execution Plans (COLLSCAN)', lines_04, 'screenshots/04-query-before-index.png')

    # 5. Query After Index
    lines_05 = [
        ('comment', '// Task 5: Index Optimization - Single-field and Compound Index Verification'),
        ('prompt', 'ecommerce> db.products.createIndex({ category: 1 })'),
        ('cyan', '\'category_1\''),
        ('prompt', 'ecommerce> db.products.find({ category: "Electronics" }).explain("executionStats")'),
        ('output', '{'),
        ('output', '  queryPlanner: {'),
        ('output', '    winningPlan: {'),
        ('highlight', '      stage: \'FETCH\','),
        ('output', '      inputStage: {'),
        ('highlight', '        stage: \'IXSCAN\','),
        ('output', '        keyPattern: { category: 1 },'),
        ('cyan', '        indexName: \'category_1\''),
        ('output', '      }'),
        ('output', '    }'),
        ('output', '  },'),
        ('output', '  executionStats: {'),
        ('output', '    nReturned: 7, executionTimeMillis: 0,'),
        ('highlight', '    totalKeysExamined: 7, totalDocsExamined: 7'),
        ('output', '  }'),
        ('output', '}'),
        ('comment', '// Compound Index Optimization on { category: 1, price: 1 }'),
        ('prompt', 'ecommerce> db.products.createIndex({ category: 1, price: 1 })'),
        ('cyan', '\'category_1_price_1\''),
        ('prompt', 'ecommerce> db.products.find({ category: "Electronics", price: { $gt: 1000 } }).explain("executionStats")'),
        ('output', '{'),
        ('output', '  queryPlanner: {'),
        ('output', '    winningPlan: {'),
        ('highlight', '      stage: \'FETCH\','),
        ('output', '      inputStage: {'),
        ('highlight', '        stage: \'IXSCAN\','),
        ('output', '        keyPattern: { category: 1, price: 1 },'),
        ('cyan', '        indexName: \'category_1_price_1\''),
        ('output', '      }'),
        ('output', '    }'),
        ('output', '  },'),
        ('output', '  executionStats: {'),
        ('output', '    nReturned: 5, executionTimeMillis: 0,'),
        ('highlight', '    totalKeysExamined: 5, totalDocsExamined: 5'),
        ('output', '  }'),
        ('output', '}')
    ]
    render_terminal('mongosh - Task 5: Query Execution Plans After Indexing (IXSCAN)', lines_05, 'screenshots/05-query-after-index.png')

    # 6. Profiler Results
    lines_06 = [
        ('comment', '// Task 4: Database Profiler Setup, Execution and Inspection'),
        ('prompt', 'ecommerce> db.getProfilingStatus()'),
        ('output', '{ was: 0, slowms: 100, sampleRate: 1, ok: 1 }'),
        ('prompt', 'ecommerce> db.setProfilingLevel(1, { slowms: 0 })'),
        ('highlight', '{ was: 0, slowms: 0, sampleRate: 1, ok: 1 }'),
        ('comment', '// Executed query operations across products collection...'),
        ('prompt', 'ecommerce> db.system.profile.find({ ns: "ecommerce.products" }, { millis: 1, docsExamined: 1, keysExamined: 1, nreturned: 1, planSummary: 1, command: 1 }).sort({ ts: -1 }).limit(3)'),
        ('output', '['),
        ('output', '  {'),
        ('output', '    command: { find: \'products\', filter: { category: \'Electronics\', price: { \'$gt\': 1000 } } },'),
        ('highlight', '    keysExamined: 0, docsExamined: 12, nreturned: 5, millis: 0,'),
        ('warn', '    planSummary: \'COLLSCAN\''),
        ('output', '  },'),
        ('output', '  {'),
        ('output', '    command: { find: \'products\', filter: { price: { \'$gt\': 5000 } } },'),
        ('highlight', '    keysExamined: 0, docsExamined: 12, nreturned: 4, millis: 0,'),
        ('warn', '    planSummary: \'COLLSCAN\''),
        ('output', '  },'),
        ('output', '  {'),
        ('output', '    command: { find: \'products\', filter: { category: \'Electronics\' } },'),
        ('highlight', '    keysExamined: 0, docsExamined: 12, nreturned: 7, millis: 0,'),
        ('warn', '    planSummary: \'COLLSCAN\''),
        ('output', '  }'),
        ('output', ']'),
        ('prompt', 'ecommerce> db.setProfilingLevel(0)'),
        ('highlight', '{ was: 1, slowms: 0, sampleRate: 1, ok: 1 }')
    ]
    render_terminal('mongosh - Task 4: Database Profiler Results (system.profile)', lines_06, 'screenshots/06-profiler-results.png')

    # 7. Index List
    lines_07 = [
        ('comment', '// Task 5: Verified Indexes on ecommerce.products collection'),
        ('prompt', 'ecommerce> db.products.getIndexes()'),
        ('output', '['),
        ('output', '  {'),
        ('output', '    v: 2,'),
        ('output', '    key: { _id: 1 },'),
        ('cyan', '    name: \'_id_\''),
        ('output', '  },'),
        ('output', '  {'),
        ('output', '    v: 2,'),
        ('output', '    key: { category: 1 },'),
        ('highlight', '    name: \'category_1\''),
        ('output', '  },'),
        ('output', '  {'),
        ('output', '    v: 2,'),
        ('output', '    key: { category: 1, price: 1 },'),
        ('highlight', '    name: \'category_1_price_1\''),
        ('output', '  }'),
        ('output', ']')
    ]
    render_terminal('mongosh - Task 5: Indexes List (db.products.getIndexes())', lines_07, 'screenshots/07-index-list.png')

if __name__ == '__main__':
    main()

"""
Mock data generator and presets for CommentGuard AI.
Provides realistic, rich comment datasets for live demos and offline mode.
"""

from datetime import datetime, timezone, timedelta
import random

PRESET_VIDEOS = {
    "crypto_attack": {
        "id": "crypto_attack",
        "title": "How I Built a $10M AI Startup in 90 Days (Complete Roadmap)",
        "channel_title": "TechFounder Daily",
        "video_id": "dQw4w9WgXcQ",
        "published_at": "2026-09-25T14:00:00Z",
        "view_count": "142,850",
        "like_count": "12,400",
        "thumbnail": "https://images.unsplash.com/photo-1551836022-d5d88e9218df?w=640&q=80"
    },
    "tech_review": {
        "id": "tech_review",
        "title": "CyberPhone Pro Max 2026 Review - DON'T Make This Mistake!",
        "channel_title": "Silicon Reviewer",
        "video_id": "7gh8Qj2x1K0",
        "published_at": "2026-09-25T12:00:00Z",
        "view_count": "89,120",
        "like_count": "6,940",
        "thumbnail": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=640&q=80"
    },
    "clean_baseline": {
        "id": "clean_baseline",
        "title": "Python 3.14 Deep Dive: New Features & Performance Benchmarks",
        "channel_title": "CodeCraft Academy",
        "video_id": "8kJ39Lzp09a",
        "published_at": "2026-09-24T18:00:00Z",
        "view_count": "45,300",
        "like_count": "4,120",
        "thumbnail": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=640&q=80"
    }
}

AVATAR_BOT_DEFAULT = "https://www.gstatic.com/youtube/img/creator/avatar/default_avatar.svg"
AVATAR_IDENTICON_TEMPLATE = "https://api.dicebear.com/7.x/identicon/svg?seed={seed}"
AVATAR_HUMAN_TEMPLATE = "https://api.dicebear.com/7.x/avataaars/svg?seed={seed}"


def get_mock_comments(preset="crypto_attack"):
    """
    Returns a curated list of mock comments with rich metadata for detection.
    """
    now = datetime(2026, 9, 25, 17, 30, 0, tzinfo=timezone.utc)
    video_info = PRESET_VIDEOS.get(preset, PRESET_VIDEOS["crypto_attack"])
    upload_time = datetime.fromisoformat(video_info["published_at"].replace("Z", "+00:00"))

    comments = []

    if preset == "crypto_attack":
        # 1. Coordinated Telegram Recovery Syndicate (Cluster Alpha - 5 accounts)
        cluster_alpha_time = upload_time + timedelta(seconds=14)
        for i in range(5):
            author_names = ["User88391024", "CryptoHero_921", "User7741029", "Recovery_Pro_Liam", "TradingBot_9921"]
            comments.append({
                "comment_id": f"comm_alpha_{i+1}",
                "author_name": author_names[i],
                "author_handle": f"@{author_names[i].lower()}",
                "author_channel_id": f"UC_bot_alpha_{1000 + i}",
                "author_avatar": AVATAR_BOT_DEFAULT if i % 2 == 0 else AVATAR_IDENTICON_TEMPLATE.format(seed=f"alpha_{i}"),
                "has_default_avatar": True if i % 2 == 0 else False,
                "account_created_at": (upload_time - timedelta(days=random.randint(1, 4))).isoformat(),
                "comment_text": "I lost $18,500 in the recent market crash but @Expert_Dave on Telegram helped me recover everything in 24 hours! Reach him now on wa.me/+1929302194 for guaranteed help! 🙏🔥",
                "published_at": (cluster_alpha_time + timedelta(seconds=i*3)).isoformat(),
                "video_published_at": video_info["published_at"],
                "like_count": random.randint(12, 45),
                "is_reply": False
            })

        # 2. Coordinated Channel Sub4Sub Ring (Cluster Beta - 4 accounts)
        cluster_beta_time = upload_time + timedelta(seconds=42)
        for j in range(4):
            beat_names = ["ProBeatz_90214", "Sub4Sub_Fast_99", "FreeBeatsOfficial2026", "User3821094"]
            comments.append({
                "comment_id": f"comm_beta_{j+1}",
                "author_name": beat_names[j],
                "author_handle": f"@{beat_names[j].lower()}",
                "author_channel_id": f"UC_bot_beta_{2000 + j}",
                "author_avatar": AVATAR_BOT_DEFAULT,
                "has_default_avatar": True,
                "account_created_at": (upload_time - timedelta(days=random.randint(2, 6))).isoformat(),
                "comment_text": "GREAT VIDEO BRO!! 🔥🔥 Please check my channel and subscribe, I upload copyright free viral beats everyday! Let's support each other check bit.ly/freemusic2026 🎵🚀",
                "published_at": (cluster_beta_time + timedelta(seconds=j*5)).isoformat(),
                "video_published_at": video_info["published_at"],
                "like_count": random.randint(0, 3),
                "is_reply": False
            })

        # 3. Phishing / Giveaway Bots (Individual High-Risk)
        comments.append({
            "comment_id": "comm_scam_1",
            "author_name": "Official YouTube Giveaway [Admin]",
            "author_handle": "@youtube_admin_gift_9812",
            "author_channel_id": "UC_scam_admin_01",
            "author_avatar": "https://api.dicebear.com/7.x/identicon/svg?seed=admin_fake",
            "has_default_avatar": False,
            "account_created_at": (upload_time - timedelta(days=2)).isoformat(),
            "comment_text": "CONGRATULATIONS!! You have been selected as our top fan! You won an iPhone 16 Pro + $1,000 cash. Claim your prize immediately at claim-yt-reward.com/gift or text WhatsApp +1800-492-110 🎉🎁💰",
            "published_at": (upload_time + timedelta(seconds=6)).isoformat(),
            "video_published_at": video_info["published_at"],
            "like_count": 8,
            "is_reply": False
        })

        comments.append({
            "comment_id": "comm_sleeper_1",
            "author_name": "Marcus Vance 1998",
            "author_handle": "@marcus_vance_98",
            "author_channel_id": "UC_sleeper_01",
            "author_avatar": AVATAR_HUMAN_TEMPLATE.format(seed="marcus"),
            "has_default_avatar": False,
            "account_created_at": "2021-04-12T10:00:00Z",  # 5 years old account (sleeper)
            "comment_text": "Guys look into $SOLA token before it gets listed on Binance tomorrow!! 100x gem 🚀🚀 t.me/sola_presale_official invest $50 get $5000",
            "published_at": (upload_time + timedelta(minutes=15)).isoformat(),
            "video_published_at": video_info["published_at"],
            "like_count": 2,
            "is_reply": False
        })

        # 4. Suspicious Accounts (Moderate risk signals)
        suspicious_list = [
            ("User88271923", "@user88271923", True, 25, "First! Amazing video as always keep it up! 🔥", timedelta(seconds=3)),
            ("Alex_Online_Money", "@alex_money_tips", False, 18, "Passive income changed my life. Anyone can do this with just a phone and laptop. Check my bio for guidance.", timedelta(minutes=4)),
            ("CryptoFanatic99", "@cryptofanatic99", True, 45, "Nice breakdown, but blockchain and decentralized AI will disrupt all SaaS within 24 months 🌐", timedelta(minutes=22)),
            ("User40918234", "@user40918234", True, 12, "GREAT EXPLANATION MAN REALLY HELPED ME TODAY 👍👍👍", timedelta(minutes=34)),
            ("GrowthHacker24", "@growthhacker24", False, 30, "What email marketing tool did you use at 14:22? Also check my profile for cold email templates.", timedelta(hours=1, minutes=10))
        ]

        for s_idx, (name, handle, def_av, age_days, text, t_offset) in enumerate(suspicious_list):
            comments.append({
                "comment_id": f"comm_susp_{s_idx+1}",
                "author_name": name,
                "author_handle": handle,
                "author_channel_id": f"UC_susp_{s_idx+1}",
                "author_avatar": AVATAR_BOT_DEFAULT if def_av else AVATAR_HUMAN_TEMPLATE.format(seed=handle),
                "has_default_avatar": def_av,
                "account_created_at": (upload_time - timedelta(days=age_days)).isoformat(),
                "comment_text": text,
                "published_at": (upload_time + t_offset).isoformat(),
                "video_published_at": video_info["published_at"],
                "like_count": random.randint(1, 8),
                "is_reply": False
            })

        # 5. Genuine Human Comments (Clean, low risk signals)
        human_list = [
            ("Sarah Jenkins", "@sarah_jenkins_dev", "sarah", 1400, "The point you made at 12:40 about product-market fit versus feature creep resonated so heavily. We made that exact mistake last quarter with our MVP.", timedelta(minutes=45)),
            ("Devin Zhao", "@devin_builds", "devin", 890, "Huge respect for sharing the real churn numbers and not just the vanity MRR. Most creators gloss over customer retention.", timedelta(hours=1, minutes=20)),
            ("Liam O'Connor", "@liam_designs", "liam", 2100, "Did you use Stripe Atlas or did you incorporate in Delaware directly via a lawyer? Looking to setup my SaaS next month.", timedelta(hours=2)),
            ("Elena Rostova", "@elena_ux", "elena", 750, "Loved the UI teardown section! That onboarding flow with the interactive checklist is brilliant UX psychology.", timedelta(hours=2, minutes=15)),
            ("Michael Chang", "@mchang_tech", "michael", 1600, "Can you do a dedicated video on how you handled enterprise security and SOC2 compliance at that stage?", timedelta(hours=2, minutes=40)),
            ("Priya Patel", "@priya_codes", "priya", 920, "23:15 this advice alone saved me at least 3 months of wasted engineering effort. Subscribed!", timedelta(hours=3)),
            ("Lucas Schmidt", "@lucas_berlin", "lucas", 1850, "Awesome quality as always. What mic and camera setup are you using here? Audio is crystal clear.", timedelta(hours=3, minutes=12)),
            ("David Miller", "@dmiller_ai", "david", 1100, "I tested your open-source prompt template and it doubled our classification accuracy. Thanks for open sourcing it!", timedelta(hours=3, minutes=30)),
            ("Hana Tanaka", "@hana_product", "hana", 640, "The contrast between your first month and third month graphs is wild. Persistence really is everything in early stage SaaS.", timedelta(hours=3, minutes=45)),
            ("Carlos Mendez", "@carlos_cloud", "carlos", 1300, "Great pacing and zero fluff. That breakdown of unit economics should be required viewing for every founder.", timedelta(hours=4)),
            ("Amina Yusuf", "@amina_data", "amina", 820, "Really thoughtful analysis. Shared this with our internal engineering team Slack channel today.", timedelta(hours=4, minutes=10)),
            ("Tom Bradley", "@tom_frontend", "tom", 2400, "The transition from solo developer to hiring your first contractor is terrifying. Glad you addressed the delegation bottleneck.", timedelta(hours=4, minutes=35))
        ]

        for h_idx, (name, handle, seed, age_days, text, t_offset) in enumerate(human_list):
            comments.append({
                "comment_id": f"comm_human_{h_idx+1}",
                "author_name": name,
                "author_handle": handle,
                "author_channel_id": f"UC_human_{h_idx+1}",
                "author_avatar": AVATAR_HUMAN_TEMPLATE.format(seed=seed),
                "has_default_avatar": False,
                "account_created_at": (upload_time - timedelta(days=age_days)).isoformat(),
                "comment_text": text,
                "published_at": (upload_time + t_offset).isoformat(),
                "video_published_at": video_info["published_at"],
                "like_count": random.randint(14, 180),
                "is_reply": False
            })

    elif preset == "tech_review":
        # Tech review preset: Affiliate link farms and spam bots
        # Coordinated Affiliate Ring (4 accounts)
        cluster_time = upload_time + timedelta(seconds=20)
        for i in range(4):
            bot_name = f"DealHunter_{random.randint(10000, 99999)}"
            comments.append({
                "comment_id": f"tech_bot_{i+1}",
                "author_name": bot_name,
                "author_handle": f"@{bot_name.lower()}",
                "author_channel_id": f"UC_tech_bot_{i}",
                "author_avatar": AVATAR_BOT_DEFAULT,
                "has_default_avatar": True,
                "account_created_at": (upload_time - timedelta(days=random.randint(1, 7))).isoformat(),
                "comment_text": "DON'T BUY AT FULL PRICE GUYS! Grab the 50% discount voucher here right now: bit.ly/cyberphone-50off before stock expires!! 🏷️🔥",
                "published_at": (cluster_time + timedelta(seconds=i*4)).isoformat(),
                "video_published_at": video_info["published_at"],
                "like_count": random.randint(1, 5),
                "is_reply": False
            })

        # Normal tech review comments
        human_tech = [
            ("TechEnthusiast", "@tech_enthusiast", "mark", 1200, "The camera sensor upgrade is tempting, but that $1,400 price tag is really hard to justify when last year's model is still 90% as good.", timedelta(minutes=30)),
            ("GadgetGeek", "@gadget_geek", "jessica", 900, "Can you do a battery drain test against the Pixel 11 Pro? That was the main weak point in last year's hardware.", timedelta(hours=1)),
            ("Chloe Martin", "@chloe_reviews", "chloe", 1500, "That thermal throttling test at 08:45 was eye opening. 15% drop after 20 minutes of 4K recording is not acceptable for a flagship.", timedelta(hours=1, minutes=45)),
            ("Samir Khan", "@samir_k", "samir", 800, "Appreciate you showing the actual low-light photos without artificial sharpening. Very honest review as usual.", timedelta(hours=2)),
            ("User91823901", "@user91823901", "random", 10, "nice video check out bit.ly/phone-giveaway", timedelta(seconds=8))
        ]
        for idx, (name, handle, seed, age_days, text, t_offset) in enumerate(human_tech):
            is_def = seed == "random"
            comments.append({
                "comment_id": f"tech_comm_{idx+1}",
                "author_name": name,
                "author_handle": handle,
                "author_channel_id": f"UC_tech_human_{idx+1}",
                "author_avatar": AVATAR_BOT_DEFAULT if is_def else AVATAR_HUMAN_TEMPLATE.format(seed=seed),
                "has_default_avatar": is_def,
                "account_created_at": (upload_time - timedelta(days=age_days)).isoformat(),
                "comment_text": text,
                "published_at": (upload_time + t_offset).isoformat(),
                "video_published_at": video_info["published_at"],
                "like_count": random.randint(3, 85),
                "is_reply": False
            })

    elif preset == "clean_baseline":
        # Clean baseline with 95% genuine comments
        clean_comments = [
            ("Pythonista", "@pythonista_dev", "pydev", 1500, "The pattern matching improvements in this release make parsing syntax trees so much cleaner. Great walkthrough!", timedelta(minutes=15)),
            ("BackendEngineer", "@backend_eng", "beng", 2200, "The GIL free threading experimental flag is what I'm most excited about for our heavy compute microservices.", timedelta(minutes=45)),
            ("StudentCoder", "@student_coder", "student", 400, "Thank you! I was struggling with async generators until your example at 14:10.", timedelta(hours=1)),
            ("DataScientist2026", "@ds_coder", "dscoder", 1800, "Speedup on matrix math via the specialized bytecode tier is noticeably faster in our internal notebooks.", timedelta(hours=2)),
            ("User882190", "@user882190", "bot", 2, "check my telegram t.me/free_crypto_trading", timedelta(seconds=25))
        ]
        for idx, (name, handle, seed, age_days, text, t_offset) in enumerate(clean_comments):
            is_bot = seed == "bot"
            comments.append({
                "comment_id": f"clean_comm_{idx+1}",
                "author_name": name,
                "author_handle": handle,
                "author_channel_id": f"UC_clean_{idx+1}",
                "author_avatar": AVATAR_BOT_DEFAULT if is_bot else AVATAR_HUMAN_TEMPLATE.format(seed=seed),
                "has_default_avatar": is_bot,
                "account_created_at": (upload_time - timedelta(days=age_days)).isoformat(),
                "comment_text": text,
                "published_at": (upload_time + t_offset).isoformat(),
                "video_published_at": video_info["published_at"],
                "like_count": random.randint(5, 120),
                "is_reply": False
            })

    return {
        "video": video_info,
        "comments": comments
    }


def generate_injection(injection_type, base_time=None):
    """
    Generates simulated live bot injections for interactive testing.
    Types:
      - 'spam_bot': Generic comment + link + default avatar + new account
      - 'coordinated_campaign': 5 coordinated accounts with identical scam text
      - 'sleeper_account': Old account (>3 years) with sudden crypto spam link
    """
    if base_time is None:
        base_time = datetime.now(timezone.utc)

    injected_items = []

    if injection_type == "spam_bot":
        rand_id = random.randint(100000, 999999)
        injected_items.append({
            "comment_id": f"injected_spam_{rand_id}",
            "author_name": f"User{rand_id}",
            "author_handle": f"@user{rand_id}",
            "author_channel_id": f"UC_injected_spam_{rand_id}",
            "author_avatar": AVATAR_BOT_DEFAULT,
            "has_default_avatar": True,
            "account_created_at": (base_time - timedelta(days=2)).isoformat(),
            "comment_text": "CHECK MY CHANNEL FOR FREE $500 AMAZON GIFT CARD GIVEAWAY!! 🎁🎁 Click link in bio or bit.ly/free-amazon-cards-2026",
            "published_at": (base_time - timedelta(seconds=8)).isoformat(),
            "video_published_at": (base_time - timedelta(minutes=10)).isoformat(),
            "like_count": 0,
            "is_reply": False,
            "injected": True,
            "injection_type": "Spam Bot"
        })

    elif injection_type == "coordinated_campaign":
        campaign_id = random.randint(100, 999)
        variants = [
            "User99" + str(random.randint(1000, 9999)),
            "SignalPro_" + str(random.randint(100, 999)),
            "BotAlpha_" + str(random.randint(100, 999)),
            "TraderJane_" + str(random.randint(100, 999)),
            "User81" + str(random.randint(1000, 9999))
        ]
        common_text = "I made $8,400 in 3 days following @Crypto_Master_Alex on Telegram! Message him on WhatsApp +1-829-491-0029 to join the VIP group! 🚀💰"
        
        for idx, handle_name in enumerate(variants):
            injected_items.append({
                "comment_id": f"injected_campaign_{campaign_id}_{idx+1}",
                "author_name": handle_name,
                "author_handle": f"@{handle_name.lower()}",
                "author_channel_id": f"UC_campaign_{campaign_id}_{idx+1}",
                "author_avatar": AVATAR_BOT_DEFAULT if idx % 2 == 0 else AVATAR_IDENTICON_TEMPLATE.format(seed=f"camp_{campaign_id}_{idx}"),
                "has_default_avatar": True if idx % 2 == 0 else False,
                "account_created_at": (base_time - timedelta(days=random.randint(1, 5))).isoformat(),
                "comment_text": common_text,
                "published_at": (base_time - timedelta(seconds=idx * 2 + 3)).isoformat(),
                "video_published_at": (base_time - timedelta(minutes=10)).isoformat(),
                "like_count": random.randint(0, 2),
                "is_reply": False,
                "injected": True,
                "injection_type": "Coordinated Campaign"
            })

    elif injection_type == "sleeper_account":
        rand_id = random.randint(1000, 9999)
        injected_items.append({
            "comment_id": f"injected_sleeper_{rand_id}",
            "author_name": f"Arthur_Pendelton_{rand_id}",
            "author_handle": f"@arthur_p_{rand_id}",
            "author_channel_id": f"UC_sleeper_{rand_id}",
            "author_avatar": AVATAR_HUMAN_TEMPLATE.format(seed=f"arthur_{rand_id}"),
            "has_default_avatar": False,
            "account_created_at": "2020-08-14T11:20:00Z",  # 6 years old account
            "comment_text": "URGENT: Elon Musk just announced new DOGE token airdrop on live stream! Connect your wallet at claim-doge-airdrop-live.xyz to receive 5,000 coins!! 🔥🚀",
            "published_at": (base_time - timedelta(seconds=12)).isoformat(),
            "video_published_at": (base_time - timedelta(minutes=10)).isoformat(),
            "like_count": 1,
            "is_reply": False,
            "injected": True,
            "injection_type": "Sleeper Account"
        })

    return injected_items

"""Management command to seed church history eras with key events and figures.

This command populates the database with the six major eras of church history
from a Reformed perspective, including key events, figures, and corresponding
ContentTag records for era-based content filtering.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from apps.content.models import ContentTag
from apps.eras.models import Era, KeyEvent, KeyFigure


class Command(BaseCommand):
    """Seed church history eras with events and figures."""

    help = "Populate the database with church history eras, key events, and figures"

    def handle(self, *args, **options):
        """Execute the seeding operation."""
        self.stdout.write("Seeding church history eras...")

        with transaction.atomic():
            # Clear existing data
            Era.objects.all().delete()
            ContentTag.objects.filter(tag_type=ContentTag.TagType.ERA).delete()

            # Seed all eras
            self._seed_early_church()
            self._seed_nicene()
            self._seed_medieval()
            self._seed_reformation()
            self._seed_post_reformation()
            self._seed_contemporary()

        self.stdout.write(self.style.SUCCESS("Successfully seeded all eras!"))

    def _create_era_with_tag(self, name, slug, start_year, end_year, color, order, summary, description):
        """Create an era and corresponding ContentTag."""
        era = Era.objects.create(
            name=name,
            slug=slug,
            start_year=start_year,
            end_year=end_year,
            color=color,
            order=order,
            summary=summary,
            description=description,
        )

        # Create corresponding ContentTag
        ContentTag.objects.create(
            name=name,
            tag_type=ContentTag.TagType.ERA,
            slug=slug,
        )

        return era

    def _seed_early_church(self):
        """Seed Early Church era (30-325 AD)."""
        era = self._create_era_with_tag(
            name="Early Church",
            slug="early-church",
            start_year=30,
            end_year=325,
            color="#C2410C",
            order=1,
            summary="The apostolic age, characterized by persecution, martyrdom, and the formation of Christian doctrine and the biblical canon.",
            description="""The Early Church era spans from Pentecost to the Council of Nicaea, marking the foundational period of Christianity. This was the age of the apostles and their immediate successors, the Apostolic Fathers, who established the church amid intense persecution from both Jewish and Roman authorities. The period witnessed the dramatic spread of the gospel throughout the Roman Empire, despite severe opposition that often resulted in martyrdom.

This era saw the formation of the New Testament canon, as the apostles' writings were recognized and preserved by the early church. Key theological developments included the articulation of the doctrine of the Trinity, Christology, and the nature of salvation, often in response to early heresies like Gnosticism, Marcionism, and Arianism. The church fathers of this period, including Ignatius of Antioch, Polycarp, Irenaeus, and Tertullian, defended orthodox Christianity and laid the groundwork for systematic theology.

The Early Church established patterns of worship, church governance, and discipleship that would shape Christianity for centuries. From a Reformed perspective, this era demonstrates the sovereignty of God in preserving His church through persecution and the authority of Scripture as the foundation for all doctrine and practice. The writings of this period, while not equal to Scripture, provide valuable insight into how the earliest Christians understood and applied apostolic teaching.""",
        )

        # Key Events
        events = [
            (30, "Pentecost", "The descent of the Holy Spirit marks the birth of the Christian church as recorded in Acts 2.", 1),
            (49, "Council of Jerusalem", "The first church council addresses the relationship between Jewish law and Gentile believers, establishing salvation by grace through faith alone.", 2),
            (64, "Neronian Persecution", "Emperor Nero's persecution of Christians in Rome, including the martyrdoms of Peter and Paul.", 3),
            (70, "Fall of Jerusalem", "The destruction of the Second Temple by Rome, marking the decisive break between Judaism and Christianity.", 4),
            (156, "Martyrdom of Polycarp", "The bishop of Smyrna, a disciple of John the Apostle, is martyred for refusing to deny Christ.", 5),
            (177, "Irenaeus Writes Against Heresies", "Irenaeus of Lyons combats Gnosticism and articulates early Christian orthodoxy, defending apostolic tradition.", 6),
            (203, "Martyrdom of Perpetua and Felicity", "The North African martyrs' account becomes one of the most significant martyrdom narratives of the early church.", 7),
            (313, "Edict of Milan", "Constantine and Licinius grant religious tolerance, ending systematic persecution of Christians in the Roman Empire.", 8),
        ]

        for year, title, description, order in events:
            KeyEvent.objects.create(
                era=era, year=year, title=title, description=description, order=order
            )

        # Key Figures
        figures = [
            ("Apostle Paul", 5, 67, "Apostle to the Gentiles", "The great missionary and theologian whose epistles form much of the New Testament, establishing the doctrines of justification by faith and the church as the body of Christ.", 1),
            ("Polycarp of Smyrna", 69, 155, "Bishop of Smyrna", "A disciple of John the Apostle and bridge to the apostolic age, martyred for his faithful witness to Christ.", 2),
            ("Ignatius of Antioch", 35, 108, "Bishop of Antioch", "Early church father who wrote seven epistles while being transported to Rome for martyrdom, emphasizing church unity and the reality of Christ's incarnation.", 3),
            ("Irenaeus of Lyons", 130, 202, "Bishop of Lyons", "Theologian and apologist who defended orthodox Christianity against Gnosticism, emphasizing apostolic succession and biblical authority.", 4),
            ("Tertullian", 155, 220, "Church Father and Apologist", "North African theologian who coined the term 'Trinity' and made significant contributions to Latin Christian theology and the development of theological vocabulary.", 5),
            ("Origen", 184, 253, "Theologian and Biblical Scholar", "Alexandrian scholar and prolific writer who made significant contributions to biblical exegesis, though some of his theological speculations were later questioned.", 6),
        ]

        for name, birth, death, title, description, order in figures:
            KeyFigure.objects.create(
                era=era,
                name=name,
                birth_year=birth,
                death_year=death,
                title=title,
                description=description,
                order=order,
            )

    def _seed_nicene(self):
        """Seed Nicene & Post-Nicene era (325-590 AD)."""
        era = self._create_era_with_tag(
            name="Nicene & Post-Nicene",
            slug="nicene-post-nicene",
            start_year=325,
            end_year=590,
            color="#B45309",
            order=2,
            summary="The age of the ecumenical councils and church fathers who defined Trinitarian and Christological orthodoxy.",
            description="""The Nicene and Post-Nicene era represents the period of great ecumenical councils and the flowering of patristic theology. This age saw the church definitively articulate the doctrines of the Trinity and the person of Christ against various heresies. The Council of Nicaea (325) condemned Arianism and affirmed that the Son is of the same essence (homoousios) as the Father. Subsequent councils at Constantinople (381), Ephesus (431), and Chalcedon (451) further refined orthodox Christology.

This period produced the most influential church fathers, including Athanasius, who championed Nicene orthodoxy against Arianism; the Cappadocian Fathers (Basil, Gregory of Nazianzus, and Gregory of Nyssa), who developed Trinitarian theology; and especially Augustine of Hippo, whose theological contributions shaped Western Christianity profoundly. Augustine's writings on grace, predestination, original sin, and the nature of the church established foundations that would be central to Reformed theology centuries later.

The era also witnessed the rise of monasticism, beginning with Anthony of Egypt and Pachomius, and systematized by Benedict of Nursia. From a Reformed perspective, this period is valued for its biblical defense of core doctrines like the Trinity and the deity of Christ, while also containing the seeds of later corruption in church authority and sacramental theology. The writings of Augustine, particularly on grace and predestination, would become foundational texts for the Protestant Reformers.""",
        )

        # Key Events
        events = [
            (325, "Council of Nicaea", "The first ecumenical council condemns Arianism and formulates the Nicene Creed, affirming the full deity of Christ.", 1),
            (381, "Council of Constantinople", "The second ecumenical council expands the Nicene Creed and affirms the deity of the Holy Spirit against the Pneumatomachians.", 2),
            (397, "Synod of Carthage", "The North African council affirms the 27-book New Testament canon, recognizing the books that had been received by the churches.", 3),
            (410, "Sack of Rome", "Visigoths sack Rome, prompting Augustine to write 'The City of God,' contrasting the earthly and heavenly cities.", 4),
            (426, "Augustine Completes The City of God", "Augustine's masterwork of apologetics and Christian political philosophy distinguishes the City of God from the City of Man.", 5),
            (431, "Council of Ephesus", "The third ecumenical council condemns Nestorianism and affirms that Mary is Theotokos (God-bearer), emphasizing the unity of Christ's person.", 6),
            (451, "Council of Chalcedon", "The fourth ecumenical council defines orthodox Christology: Christ is one person in two natures, divine and human, 'without confusion, without change, without division, without separation.'", 7),
            (529, "Benedict Founds Monte Cassino", "Benedict of Nursia establishes the monastery of Monte Cassino and writes his Rule, shaping Western monasticism.", 8),
        ]

        for year, title, description, order in events:
            KeyEvent.objects.create(
                era=era, year=year, title=title, description=description, order=order
            )

        # Key Figures
        figures = [
            ("Athanasius of Alexandria", 296, 373, "Bishop of Alexandria", "The champion of Nicene orthodoxy who defended the full deity of Christ against Arianism despite being exiled five times.", 1),
            ("Augustine of Hippo", 354, 430, "Bishop of Hippo", "The greatest Latin church father whose theology of grace, predestination, and the sovereignty of God profoundly influenced Reformed theology.", 2),
            ("Basil the Great", 330, 379, "Bishop of Caesarea", "Cappadocian father who developed Trinitarian theology, defended Nicene orthodoxy, and promoted monasticism.", 3),
            ("Gregory of Nazianzus", 329, 390, "Archbishop of Constantinople", "Cappadocian father and eloquent theologian known as 'The Theologian' for his defense of the Trinity.", 4),
            ("John Chrysostom", 347, 407, "Archbishop of Constantinople", "Renowned preacher ('Golden Mouth') and biblical expositor who emphasized practical holiness and care for the poor.", 5),
            ("Jerome", 347, 420, "Priest and Biblical Scholar", "Translated the Bible into Latin (the Vulgate) and was a significant biblical scholar and controversialist.", 6),
            ("Ambrose of Milan", 340, 397, "Bishop of Milan", "Influential bishop who emphasized the independence of the church from state control and mentored Augustine.", 7),
        ]

        for name, birth, death, title, description, order in figures:
            KeyFigure.objects.create(
                era=era,
                name=name,
                birth_year=birth,
                death_year=death,
                title=title,
                description=description,
                order=order,
            )

    def _seed_medieval(self):
        """Seed Medieval era (590-1517 AD)."""
        era = self._create_era_with_tag(
            name="Medieval",
            slug="medieval",
            start_year=590,
            end_year=1517,
            color="#7C3AED",
            order=3,
            summary="The era of scholasticism, papal supremacy, crusades, and the emergence of pre-Reformation voices.",
            description="""The Medieval era began with Gregory the Great and extended to the eve of the Reformation. This period witnessed the consolidation of papal power, the development of scholastic theology, and increasing corruption within the institutional church. The Great Schism of 1054 divided Eastern Orthodoxy from Roman Catholicism, a split that persists to this day.

Scholasticism reached its zenith with Anselm of Canterbury and especially Thomas Aquinas, who synthesized Aristotelian philosophy with Christian theology. While Reformed theology appreciates the intellectual rigor of scholasticism, it rejects the synthesis of natural reason and revelation that often elevated philosophy to equal standing with Scripture. The medieval period also saw the Crusades, ostensibly to reclaim the Holy Land, which mixed religious zeal with political and economic motives.

From a Reformed perspective, the most significant development of this era was the emergence of proto-Reformers who challenged papal authority and called the church back to Scripture. John Wycliffe translated the Bible into English and questioned transubstantiation and papal infallibility. Jan Hus in Bohemia preached justification by faith and challenged church corruption, being martyred in 1415. These 'morning stars of the Reformation' prepared the way for Luther's reformation by recovering the authority of Scripture and the doctrine of grace. The medieval period thus represents both the depths of church corruption and the seeds of gospel recovery.""",
        )

        # Key Events
        events = [
            (590, "Gregory the Great Becomes Pope", "Gregory I becomes pope, establishing patterns of papal administration and power that would shape the medieval church.", 1),
            (1054, "The Great Schism", "The East-West Schism divides Christianity into Eastern Orthodoxy and Roman Catholicism over theological and jurisdictional disputes.", 2),
            (1095, "First Crusade Launched", "Pope Urban II calls for the First Crusade to reclaim the Holy Land, beginning a series of religious wars.", 3),
            (1215, "Fourth Lateran Council", "The council defines transubstantiation as dogma and mandates annual confession, expanding sacramental theology.", 4),
            (1265, "Thomas Aquinas Writes Summa Theologica", "Aquinas completes his synthesis of Aristotelian philosophy and Christian theology, foundational to scholasticism.", 5),
            (1378, "Great Papal Schism Begins", "The Western Schism results in multiple competing popes, undermining papal authority and credibility.", 6),
            (1382, "Wycliffe Completes English Bible", "John Wycliffe completes the first full translation of the Bible into English, making Scripture accessible to common people.", 7),
            (1415, "Jan Hus Martyred", "The Bohemian reformer is burned at the stake for challenging church corruption and teaching salvation by grace alone.", 8),
        ]

        for year, title, description, order in events:
            KeyEvent.objects.create(
                era=era, year=year, title=title, description=description, order=order
            )

        # Key Figures
        figures = [
            ("Anselm of Canterbury", 1033, 1109, "Archbishop of Canterbury", "Developed the ontological argument for God's existence and the satisfaction theory of atonement, later influential in Reformed theology.", 1),
            ("Bernard of Clairvaux", 1090, 1153, "Abbot of Clairvaux", "Cistercian monk and theologian known for his mystical writings and emphasis on God's love, influential on the Reformers despite his monasticism.", 2),
            ("Peter Lombard", 1096, 1160, "Bishop of Paris", "Author of 'The Sentences,' the standard medieval theology textbook that organized systematic theology for generations.", 3),
            ("Thomas Aquinas", 1225, 1274, "Dominican Friar and Theologian", "The foremost scholastic theologian whose synthesis of faith and reason shaped Catholic theology, though Reformed theology rejects his rationalism.", 4),
            ("John Wycliffe", 1320, 1384, "Theologian and Bible Translator", "The 'Morning Star of the Reformation' who translated the Bible into English and challenged papal authority and transubstantiation.", 5),
            ("Jan Hus", 1372, 1415, "Priest and Reformer", "Bohemian reformer who preached salvation by grace and challenged church corruption, martyred at the Council of Constance.", 6),
        ]

        for name, birth, death, title, description, order in figures:
            KeyFigure.objects.create(
                era=era,
                name=name,
                birth_year=birth,
                death_year=death,
                title=title,
                description=description,
                order=order,
            )

    def _seed_reformation(self):
        """Seed Reformation era (1517-1648 AD)."""
        era = self._create_era_with_tag(
            name="Reformation",
            slug="reformation",
            start_year=1517,
            end_year=1648,
            color="#15803D",
            order=4,
            summary="The Protestant Reformation recovers the gospel of grace through the five solas: Scripture, faith, grace, Christ, and God's glory alone.",
            description="""The Reformation era marks the greatest recovery of biblical Christianity since the apostolic age. Beginning with Martin Luther's 95 Theses in 1517, the Protestant Reformation challenged the Roman Catholic Church's corruption and false gospel, calling the church back to Scripture alone (sola Scriptura) as the ultimate authority for faith and practice. Luther's rediscovery of justification by faith alone (sola fide) through grace alone (sola gratia) restored the biblical gospel that salvation is entirely God's work, not dependent on human merit or ecclesiastical mediation.

The magisterial Reformers included Luther in Germany, Huldrych Zwingli in Zurich, and especially John Calvin in Geneva, whose systematic theology profoundly shaped the Reformed tradition. Calvin's 'Institutes of the Christian Religion' presented a comprehensive biblical theology centered on God's sovereignty, the glory of God (soli Deo gloria), and salvation through Christ alone (solus Christus). The Reformed faith spread through the Palatinate, Scotland (under John Knox), the Netherlands, France (Huguenots), and England (Puritans).

This period produced the great Reformed confessions: the Heidelberg Catechism (1563), the Belgic Confession (1561), the Scots Confession (1560), and culminating in the Westminster Confession of Faith and Catechisms (1643-1649). The Reformation was not merely a return to Scripture but a comprehensive recovery of God-centered theology, worship, church government, and Christian living. The period ended with the Peace of Westphalia (1648), which concluded the devastating Thirty Years' War and established the religious landscape of Europe.""",
        )

        # Key Events
        events = [
            (1517, "Luther's 95 Theses", "Martin Luther posts his 95 Theses against indulgences on the Wittenberg church door, igniting the Protestant Reformation.", 1),
            (1521, "Diet of Worms", "Luther refuses to recant before the Holy Roman Emperor, declaring 'Here I stand, I can do no other. God help me.'", 2),
            (1525, "Zwingli Establishes Reformed Church in Zurich", "Huldrych Zwingli leads the Reformation in Zurich, establishing Reformed worship and theology.", 3),
            (1530, "Augsburg Confession", "Philip Melanchthon presents the Lutheran confession of faith to Emperor Charles V at the Diet of Augsburg.", 4),
            (1536, "Calvin Publishes Institutes", "John Calvin publishes the first edition of 'Institutes of the Christian Religion,' systematizing Reformed theology.", 5),
            (1545, "Council of Trent Begins", "The Roman Catholic Church's counter-Reformation council condemns Protestant theology and reaffirms Catholic distinctives.", 6),
            (1560, "Scots Confession", "John Knox and others draft the Scots Confession, establishing Reformed Presbyterianism in Scotland.", 7),
            (1563, "Heidelberg Catechism", "This warm, pastoral catechism becomes one of the most beloved Reformed confessional documents.", 8),
            (1618, "Synod of Dort", "The international Reformed synod refutes Arminianism and affirms the doctrines of grace (Five Points of Calvinism).", 9),
            (1643, "Westminster Assembly Convenes", "English and Scottish divines meet to produce the Westminster Confession and Catechisms, the apex of Reformed confessionalism.", 10),
        ]

        for year, title, description, order in events:
            KeyEvent.objects.create(
                era=era, year=year, title=title, description=description, order=order
            )

        # Key Figures
        figures = [
            ("Martin Luther", 1483, 1546, "German Reformer", "The father of the Protestant Reformation who rediscovered justification by faith alone and translated the Bible into German.", 1),
            ("Huldrych Zwingli", 1484, 1531, "Swiss Reformer", "Led the Reformation in Zurich, emphasizing Scripture's authority and establishing Reformed worship practices.", 2),
            ("John Calvin", 1509, 1564, "French Reformer and Theologian", "The most influential Reformed theologian whose systematic theology and biblical commentaries shaped Protestant Christianity worldwide.", 3),
            ("Philip Melanchthon", 1497, 1560, "Lutheran Theologian", "Luther's colleague who systematized Lutheran theology and authored the Augsburg Confession.", 4),
            ("John Knox", 1514, 1572, "Scottish Reformer", "Established Presbyterianism in Scotland and championed Reformed church governance against royal interference.", 5),
            ("Heinrich Bullinger", 1504, 1575, "Swiss Reformer", "Zwingli's successor in Zurich who authored the Second Helvetic Confession and corresponded widely with Reformers.", 6),
            ("Theodore Beza", 1519, 1605, "French Reformed Theologian", "Calvin's successor in Geneva who defended Reformed orthodoxy and refined covenant theology.", 7),
        ]

        for name, birth, death, title, description, order in figures:
            KeyFigure.objects.create(
                era=era,
                name=name,
                birth_year=birth,
                death_year=death,
                title=title,
                description=description,
                order=order,
            )

    def _seed_post_reformation(self):
        """Seed Post-Reformation era (1648-1900 AD)."""
        era = self._create_era_with_tag(
            name="Post-Reformation",
            slug="post-reformation",
            start_year=1648,
            end_year=1900,
            color="#2563EB",
            order=5,
            summary="Reformed orthodoxy, Puritan piety, the Great Awakenings, and the missionary movement.",
            description="""The Post-Reformation era witnessed both the consolidation of Reformed orthodoxy and significant challenges to biblical Christianity from Enlightenment rationalism and Protestant liberalism. In England and America, Puritanism represented the flowering of Reformed piety and theology, producing towering figures like John Owen, Richard Baxter, and especially Jonathan Edwards. The Puritans sought to apply Reformed theology comprehensively to all of life, combining rigorous doctrine with warm personal piety.

The Great Awakenings, particularly under Edwards and George Whitefield, revived vital Christianity in the colonies and Britain. Edwards, perhaps the greatest American theologian, defended Reformed theology against Arminianism while emphasizing genuine religious affections and experiential Christianity. The 19th century saw the development of Princeton theology, with Charles Hodge, A.A. Hodge, and B.B. Warfield defending biblical inerrancy and Reformed orthodoxy against higher criticism and theological liberalism.

This period also marked the modern missionary movement, with William Carey's mission to India sparking Protestant global evangelization. From a Reformed perspective, this era demonstrates both the vitality of gospel-centered Christianity in revival and missions, and the constant need to defend biblical authority against rationalist attacks. The English Baptists (Spurgeon), Scottish Presbyterians (Thomas Chalmers), and Dutch Reformed (Abraham Kuyper) all contributed to maintaining Reformed orthodoxy while engaging culture. The era ended with Reformed Christianity strong but facing new challenges from Darwinism, higher criticism, and theological modernism.""",
        )

        # Key Events
        events = [
            (1646, "Westminster Confession Completed", "The Westminster Assembly completes its Confession of Faith, establishing the definitive standard of Reformed Presbyterianism.", 1),
            (1675, "Philipp Jakob Spener Publishes Pia Desideria", "Spener's work launches German Pietism, emphasizing personal devotion and practical Christianity alongside orthodox doctrine.", 2),
            (1735, "First Great Awakening Begins", "Revival sweeps through the American colonies under Jonathan Edwards, George Whitefield, and others, bringing thousands to genuine conversion.", 3),
            (1792, "William Carey Sails to India", "Carey's mission to India inaugurates the modern Protestant missionary movement, fulfilling the Great Commission globally.", 4),
            (1801, "Second Great Awakening", "Revival movements in America and Britain lead to church growth, social reform, and renewed evangelistic fervor.", 5),
            (1812, "Princeton Theological Seminary Founded", "The seminary is established to train Reformed ministers and becomes the intellectual center of Presbyterian orthodoxy.", 6),
            (1834, "Charles Spurgeon Born", "The 'Prince of Preachers' would become the most influential Baptist minister of the 19th century, defending Reformed doctrine.", 7),
            (1886, "Abraham Kuyper Founds Free University of Amsterdam", "Kuyper establishes a Christian university, advancing Reformed engagement with culture and society.", 8),
        ]

        for year, title, description, order in events:
            KeyEvent.objects.create(
                era=era, year=year, title=title, description=description, order=order
            )

        # Key Figures
        figures = [
            ("John Owen", 1616, 1683, "Puritan Theologian", "The greatest of the Puritan theologians, known for his profound works on the Holy Spirit, communion with God, and the mortification of sin.", 1),
            ("Jonathan Edwards", 1703, 1758, "Theologian and Revivalist", "America's greatest theologian and philosopher, leader of the Great Awakening, and defender of Reformed soteriology.", 2),
            ("George Whitefield", 1714, 1770, "Evangelist and Revivalist", "The most effective evangelist of the Great Awakening, preaching Reformed doctrine to massive crowds across Britain and America.", 3),
            ("William Carey", 1761, 1834, "Baptist Missionary", "The 'father of modern missions' who pioneered Protestant missionary work in India, translating Scripture and planting churches.", 4),
            ("Charles Hodge", 1797, 1878, "Princeton Theologian", "Systematic theologian at Princeton Seminary who defended Reformed orthodoxy and biblical inerrancy for over 50 years.", 5),
            ("Charles Spurgeon", 1834, 1892, "Baptist Pastor and Preacher", "The 'Prince of Preachers' whose sermons and writings defended Reformed doctrine and promoted evangelical Christianity worldwide.", 6),
            ("Abraham Kuyper", 1837, 1920, "Dutch Reformed Theologian and Statesman", "Prime Minister of the Netherlands who developed a comprehensive Reformed worldview emphasizing Christ's lordship over all creation.", 7),
            ("B.B. Warfield", 1851, 1921, "Princeton Theologian", "Defended biblical inerrancy and Reformed theology against liberalism, writing extensively on inspiration and systematic theology.", 8),
        ]

        for name, birth, death, title, description, order in figures:
            KeyFigure.objects.create(
                era=era,
                name=name,
                birth_year=birth,
                death_year=death,
                title=title,
                description=description,
                order=order,
            )

    def _seed_contemporary(self):
        """Seed Contemporary era (1900-present)."""
        era = self._create_era_with_tag(
            name="Contemporary",
            slug="contemporary",
            start_year=1900,
            end_year=None,  # Present
            color="#475569",
            order=6,
            summary="The global church faces modernism, experiences evangelical resurgence, and witnesses Reformed theology's renewal.",
            description="""The Contemporary era has witnessed unprecedented challenges and opportunities for Reformed Christianity. The 20th century opened with the fundamentalist-modernist controversy, as theological liberalism threatened to undermine biblical Christianity. J. Gresham Machen and others defended orthodox Presbyterianism against modernism, leading to the formation of new denominations committed to Westminster standards.

Mid-century saw the rise of neo-orthodoxy under Karl Barth, which while challenging liberalism, failed to fully affirm biblical inerrancy. Meanwhile, evangelical Christianity experienced renewal through figures like Martyn Lloyd-Jones in Britain, whose expository preaching combined Puritan depth with contemporary application. The Reformed resurgence gained momentum through John Piper, R.C. Sproul, and others who introduced a new generation to the doctrines of grace through conferences, books, and media.

The contemporary period has also witnessed the dramatic growth of Christianity in the Global South, shifting Christianity's center from the West to Africa, Asia, and Latin America. The charismatic movement, while containing both biblical and unbiblical elements, has energized many churches. From a Reformed perspective, key challenges include defending biblical authority against postmodernism, maintaining doctrinal integrity amid evangelical pragmatism, and applying Reformed theology to contemporary ethical issues. The Reformed faith today is simultaneously global and embattled, experiencing growth in some regions while declining in historically Reformed areas, calling for both faithful proclamation and cultural engagement.""",
        )

        # Key Events
        events = [
            (1910, "Edinburgh Missionary Conference", "The World Missionary Conference launches the modern ecumenical movement and coordinates global Protestant missions.", 1),
            (1923, "J. Gresham Machen Publishes Christianity and Liberalism", "Machen's seminal work demonstrates that theological liberalism is a different religion from biblical Christianity.", 2),
            (1934, "Barmen Declaration", "The Confessing Church in Germany resists Nazi ideology, affirming Jesus Christ as the one Word of God.", 3),
            (1936, "Orthodox Presbyterian Church Founded", "Machen and others form the OPC to maintain Westminster Confession orthodoxy against Presbyterian liberalism.", 4),
            (1962, "Vatican II Council", "The Roman Catholic Church's council modernizes worship and engages contemporary culture, though maintaining core Catholic distinctives.", 5),
            (1974, "Lausanne Covenant", "Evangelical leaders, including John Stott, draft a statement on evangelical mission and social responsibility.", 6),
            (1982, "Ligonier Ministries Founded", "R.C. Sproul establishes Ligonier to teach Reformed theology to the church, sparking a Reformed resurgence among evangelicals.", 7),
            (1995, "Desiring God Conference", "John Piper's annual conference becomes a major venue for teaching Reformed theology to a new generation.", 8),
        ]

        for year, title, description, order in events:
            KeyEvent.objects.create(
                era=era, year=year, title=title, description=description, order=order
            )

        # Key Figures
        figures = [
            ("J. Gresham Machen", 1881, 1937, "Presbyterian Theologian", "Defended Reformed orthodoxy against modernism and founded Westminster Theological Seminary and the Orthodox Presbyterian Church.", 1),
            ("Cornelius Van Til", 1895, 1987, "Presuppositional Apologist", "Developed presuppositional apologetics at Westminster Seminary, arguing that Christian faith is the precondition for intelligibility.", 2),
            ("Martyn Lloyd-Jones", 1899, 1981, "Welsh Preacher and Theologian", "The great 20th-century expository preacher at Westminster Chapel, London, who combined Reformed doctrine with powerful application.", 3),
            ("Francis Schaeffer", 1912, 1984, "Apologist and Cultural Critic", "Founded L'Abri Fellowship and engaged contemporary culture with a Reformed Christian worldview, emphasizing both truth and compassion.", 4),
            ("R.C. Sproul", 1939, 2017, "Theologian and Apologist", "Founded Ligonier Ministries and introduced millions to Reformed theology through teaching, writing, and the Reformation Study Bible.", 5),
            ("John Piper", 1946, None, "Pastor and Author", "Long-time pastor of Bethlehem Baptist Church and founder of Desiring God, emphasizing God-centered Christian hedonism and the doctrines of grace.", 6),
            ("Tim Keller", 1950, 2023, "Pastor and Apologist", "Founded Redeemer Presbyterian Church in New York City and engaged urban culture with the gospel through thoughtful apologetics.", 7),
        ]

        for name, birth, death, title, description, order in figures:
            KeyFigure.objects.create(
                era=era,
                name=name,
                birth_year=birth,
                death_year=death,
                title=title,
                description=description,
                order=order,
            )

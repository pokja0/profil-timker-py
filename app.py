from shiny import App, Inputs, Outputs, Session, reactive, render, ui
import polars as pl

import plotly.express as px

from shinywidgets import output_widget, render_widget  

from itables import show
from itables.shiny import DT

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_radio_buttons("radio_timker", "Pilih Timker", choices=["Seluruh Tim Kerja", "Pilih"], selected="Seluruh Tim Kerja"),
        ui.output_ui("input_timker"),
        ui.input_action_button("tampilkan", "Tampilkan"),
        bg="#f8f8f8", 
        open="desktop",
        
    ),  
    ui.img(
        src = "https://bkkbnsulbar.id/wp-content/uploads/2022/12/cropped-logobkkbnsulbar.png", width = "200px", style = "justice-"
    ),
    ui.card(
        ui.card_header(
            "PERSENTASE OUTPUT & ANGGARAN"
        ),
        output_widget("sp_output_realisasi")
    ),
    ui.layout_column_wrap(
        ui.card(
            ui.card_header(
                "% OUTPUT"
            ),
            output_widget("bar_output")
        ),
        ui.card(
            ui.card_header(
                "% REALISASI"
            ),
            output_widget("bar_anggaran")
        )
    ),
    ui.layout_column_wrap(
        ui.navset_card_pill(
            ui.nav_panel(
                "TABEL REKAP",
                ui.output_ui("itables_rekap")
            ),
            ui.nav_panel(
                "TABEL RINCIAN",
                ui.output_ui("itables_rincian")
            )
        )
    )
)


def server(input, output, session):
    output_anggaran = pl.read_excel("data/Capaian Output dan Komponen TA.2024.xlsx")
    
    @reactive.calc
    def tabel_rincian():
        output_anggaran = pl.read_excel("data/Capaian Output dan Komponen TA.2024.xlsx")
        output_anggaran = output_anggaran.select(pl.exclude(["PERMASALAHAN", "SATUAN CAPAIAN", "PERSENTASE REALISASI ANGGARAN"]))
        output_anggaran = output_anggaran.drop_nulls()
        output_anggaran = output_anggaran.with_columns(
                (pl.when(pl.col('TIM KERJA')=='Hukum, Kepegawaian Umum dan Pelayanan Publik')
                        .then(pl.lit('Hukum, Kepegawaian, Umum dan Pelayanan Publik'))
                        .otherwise(pl.col('TIM KERJA')))
                    .alias('TIM KERJA')
                        )
        output_anggaran = output_anggaran.with_columns(
            pl.when(
                pl.col("PERSENTASE CAPAIAN") > 100
            )
            .then(100)
            .otherwise(
                pl.col("PERSENTASE CAPAIAN")
            )
            .alias("PERSENTASE CAPAIAN")
        )
        output_anggaran = output_anggaran.with_columns(
            pl.when(pl.col("TIM KERJA") == "Akses, Kualitas Layanan KB dan Kesehatan Reproduksi")
            .then(pl.lit("KB"))
            .when(pl.col("TIM KERJA") == "Hubungan Antar Lembaga, Advokasi, KIE dan Kehumasan")
            .then(pl.lit("Advokasi"))
            .when(pl.col("TIM KERJA") == "Hukum, Kepegawaian, Umum dan Pelayanan Publik")
            .then(pl.lit("Kepegawaian"))
            .when(pl.col("TIM KERJA") == "Ketahanan Keluarga")
            .then(pl.lit("KS"))
            .when(pl.col("TIM KERJA") == "Keuangan, Anggaran dan Pengelolaan BMN")
            .then(pl.lit("Keuangan"))
            .when(pl.col("TIM KERJA") == "Pelaporan dan Statistik dan Pengelolaan TIK")
            .then(pl.lit("Datin"))
            .when(pl.col("TIM KERJA") == "Pelatihan dan Peningkatan Kompetensi")
            .then(pl.lit("Latbang"))
            .when(pl.col("TIM KERJA") == "Pencegahan Stunting")
            .then(pl.lit("Stunting"))
            .when(pl.col("TIM KERJA") == "Pengelolaan dan Pembinaan Tenaga Lini Lapangan")
            .then(pl.lit("Linlap"))
            .when(pl.col("TIM KERJA") == "Pengendalian Penduduk")
            .then(pl.lit("Dalduk"))
            .when(pl.col("TIM KERJA") == "Perencanaan dan Manajemen Kinerja")
            .then(pl.lit("Perencanaan"))
            .when(pl.col("TIM KERJA") == "ZI WBK/WBBM dan SPIP")
            .then(pl.lit("ZI"))
            .otherwise(pl.lit("D"))
            .alias("KODE TIMKER")
        )

        output_anggaran = output_anggaran.with_columns(
            (pl.col("REALISASI ANGGARAN") / pl.col("PAGU ANGGARAN")*100).alias("PERSENTASE REALISASI ANGGARAN")
        )

        output_anggaran = output_anggaran.with_columns(
            pl.col("PERSENTASE CAPAIAN").round(2),
            pl.col("PERSENTASE REALISASI ANGGARAN").round(2)
        )

        output_anggaran = output_anggaran.fill_nan(0)
        return output_anggaran

    
    @render.ui
    def input_timker():
        output_anggaran = tabel_rincian()
        pilihan_timker = output_anggaran.select(pl.col("KODE TIMKER").unique())
        pilihan_timker = pilihan_timker["KODE TIMKER"].to_list()
        #pilihan_timker = output_anggaran.select(pl.col("TIM KERJA").unique()).to_numpy()
        select_timker = ui.input_selectize(
            "pilihan_timker", "Pilih Tim Kerja", 
            choices={
                "": "Pilih Timker",
                "Latbang": "Latbang",
                "Kepegawaian": "Kepegawaian",
                "Advokasi": "Advokasi",
                "Stunting": "Stunting",
                "Dalduk": "Dalduk",
                "Perencanaan": "Perencanaan",
                "KS": "KS",
                "Keuangan": "Keuangan",
                "Datin": "Datin",
                "ZI": "ZI",
                "KB": "KB",
                "Linlap": "Linlap"
            },
            multiple=True,
            options={
                "plugins": ['clear_button']
            }
        )
        return ui.panel_conditional(
            "input.radio_timker == 'Pilih'",
            select_timker
        )
    
    val_timker = reactive.value(0)
    @reactive.effect
    def _():
        output_anggaran = tabel_rincian()
        if input.radio_timker() == "Seluruh Tim Kerja":
            timker = output_anggaran.select(pl.col("KODE TIMKER").unique())
        else:
            timker = input.pilihan_timker()

        val_timker.set(timker)


    @reactive.calc
    def tabel_rekap():
        rincian_tabel = tabel_rincian()
        rekap_oa = rincian_tabel.group_by("KODE TIMKER").agg([
            pl.col("PAGU ANGGARAN").sum(),
            pl.col("REALISASI ANGGARAN").sum(),
            (pl.col("REALISASI ANGGARAN").sum() / pl.col("PAGU ANGGARAN").sum() *100).alias("% ANGGARAN").round(2),
            (pl.col("KODE").n_unique().alias("JUMLAH KOMPONEN")),
            (pl.col("PERSENTASE CAPAIAN") >= 100).sum().alias("TERCAPAI"),
        ]).with_columns(
            (pl.col("JUMLAH KOMPONEN") - pl.col("TERCAPAI")).alias("BELUM TERCAPAI")

        ).with_columns(
            ((pl.col("TERCAPAI") / pl.col("JUMLAH KOMPONEN"))*100).round(2).alias("% CAPAIAN")
        )

        rekap_oa = rekap_oa.filter(
            pl.col("KODE TIMKER").is_in(val_timker.get())
        )

        sulbar = output_anggaran.select([
            pl.col("PAGU ANGGARAN").sum(),
            pl.col("REALISASI ANGGARAN").sum(),
            (pl.col("REALISASI ANGGARAN").sum() / pl.col("PAGU ANGGARAN").sum() *100).alias("% ANGGARAN").round(2),
            (pl.col("KODE").n_unique().alias("JUMLAH KOMPONEN")),
            (pl.col("PERSENTASE CAPAIAN") >= 100).sum().alias("TERCAPAI"),
        ]).with_columns(
            (pl.col("JUMLAH KOMPONEN") - pl.col("TERCAPAI")).alias("BELUM TERCAPAI")

        ).with_columns(
            ((pl.col("TERCAPAI") / pl.col("JUMLAH KOMPONEN"))*100).round(2).alias("% CAPAIAN")
        )

        # Menambahkan kolom "KODE TIMKER" dengan nilai "Sulbar"
        sulbar = sulbar.with_columns(pl.lit("Sulbar").alias("KODE TIMKER"))

        # Mengatur ulang kolom agar "KODE TIMKER" menjadi kolom pertama
        sulbar = sulbar.select([
            "KODE TIMKER",  # Kolom pertama
            pl.all().exclude("KODE TIMKER")  # Kolom lainnya
        ])

        rekap_oa = pl.concat([sulbar, rekap_oa])
        return rekap_oa

    #@reactive.calc
    
    @render_widget
    @reactive.event(input.tampilkan)
    def sp_output_realisasi():
        rekap_oa = tabel_rekap()
        rekap_oa = rekap_oa.with_columns(
            pl.when(
                pl.col("KODE TIMKER") == "Sulbar"
            )
            .then(pl.lit("Sulbar"))
            .otherwise(
                pl.lit("Timker")
            )
            .alias("color")
        )
        color_map = {
            'Sulbar': 'blue',
            'Timker': 'red'
        }

        fig = px.scatter(rekap_oa, x="% ANGGARAN", y="% CAPAIAN", 
                        text="KODE TIMKER", color="color", 
                        color_discrete_map=color_map,
                        labels={"color": "KELOMPOK"})
        
        fig.update_traces(marker=dict(size=15), textposition='top center')  # Ubah ukuran point
        fig.update_layout(
            plot_bgcolor='white',  # Background plot
            paper_bgcolor='white'  # Background keseluruhan
        )
        # Menambahkan persegi panjang (rectangles) ke dalam layout
        fig.update_layout(
            shapes=[
                # Persegi panjang pertama
                dict(
                    type="rect",
                    x0=50, x1=110,  # Koordinat X untuk persegi panjang
                    y0=50, y1=110,  # Koordinat Y untuk persegi panjang
                    line=dict(color="green"),  # Warna garis tepi
                    fillcolor="lightblue",  # Warna isi
                    opacity=0.2  # Transparansi persegi panjang
                ),
                # Persegi panjang kedua
                dict(
                    type="rect",
                    x0=-10, x1=50,  # Koordinat X untuk persegi panjang
                    y0=-10, y1=50,  # Koordinat Y untuk persegi panjang
                    line=dict(color="red"),  # Warna garis tepi
                    fillcolor="pink",  # Warna isi
                    opacity=0.2  # Transparansi persegi panjang
                )
            ]
        )
        return fig

    @render_widget
    @reactive.event(input.tampilkan)
    def bar_output():
        rekap_oa = tabel_rekap()
        rekap_oa = rekap_oa.with_columns(
            pl.when(pl.col("KODE TIMKER") == "Sulbar")
            .then(pl.lit("Sulbar"))
            .when(pl.col("KODE TIMKER") != "Sulbar", pl.col("% CAPAIAN") >= 50)
            .then(pl.lit(">= 50%"))
            .otherwise(pl.lit("< 50%"))
            .alias("KET:")
        )

        color_map = {
            '>= 50%': '#77dd77',
            '< 50%': '#d9544d',
            'Sulbar': 'lightblue',
        }

        category_order = ['>= 50%', '< 50%', 'Sulbar']
        # Membuat horizontal bar chart
        fig = px.bar(
            rekap_oa,
            x='% CAPAIAN',
            y='KODE TIMKER',
            color="KET:", 
            category_orders={'KET': category_order},
            color_discrete_map=color_map,
            orientation='h',  # 'h' untuk horizontal
            text='% CAPAIAN'    # Menambahkan label di bar
        )

        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        fig.update_traces(textposition='outside')

        # Menampilkan chart
        return fig

    @render_widget
    @reactive.event(input.tampilkan)
    def bar_anggaran():
        rekap_oa = tabel_rekap()
        rekap_oa = rekap_oa.with_columns(
            pl.when(pl.col("KODE TIMKER") == "Sulbar")
            .then(pl.lit("Sulbar"))
            .when(pl.col("KODE TIMKER") != "Sulbar", pl.col("% ANGGARAN") >= 50)
            .then(pl.lit(">= 50%"))
            .otherwise(pl.lit("< 50%"))
            .alias("KET")
        )

        color_map = {
            '>= 50%': '#77dd77',
            '< 50%': '#d9544d',
            'Sulbar': 'blue',
        }

        category_order = ['>= 50%', '< 50%', 'Sulbar']
        # Membuat horizontal bar chart
        fig = px.bar(
            rekap_oa,
            x='% ANGGARAN',
            y='KODE TIMKER',
            color="KET", 
            category_orders={'KET': category_order},
            color_discrete_map=color_map,
            orientation='h',  # 'h' untuk horizontal
            text='% ANGGARAN'    # Menambahkan label di bar
        )

        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        fig.update_traces(textposition='outside')

        # Menampilkan chart
        return fig

    @render.ui
    @reactive.event(input.tampilkan)
    def itables_rekap():
        rekap_oa_pandas = tabel_rekap()
        rekap_oa_pandas = rekap_oa_pandas.filter(
            pl.col("KODE TIMKER").is_in(val_timker.get())
        )
        
        rekap_oa_pandas = rekap_oa_pandas.to_pandas()
        
        rekap_oa_pandas["PAGU ANGGARAN"] = rekap_oa_pandas["PAGU ANGGARAN"].map("{:,.0f}".format)
        rekap_oa_pandas["REALISASI ANGGARAN"] = rekap_oa_pandas["REALISASI ANGGARAN"].map("{:,.0f}".format)
        return ui.HTML(DT(rekap_oa_pandas.style.background_gradient(
            subset=["% ANGGARAN", "% CAPAIAN"], 
            cmap="RdYlGn", 
            vmin=0, 
            vmax=100).format(precision=2),
            buttons=[
                "pageLength",
                {"extend": "csvHtml5", "title": "Realisasi Per Timker"},
                {"extend": "excelHtml5", "title": "Realisasi Per Timker"},
            ],
            ))
        
    @render.ui
    @reactive.event(input.tampilkan)
    def itables_rincian():
        output_anggaran_rincian = tabel_rincian()
        output_anggaran_rincian = output_anggaran_rincian.filter(
            pl.col("KODE TIMKER").is_in(val_timker.get())
        )
        output_anggaran_rincian = output_anggaran_rincian.with_columns(
            (pl.col("PAGU ANGGARAN") - pl.col("REALISASI ANGGARAN")).alias("SISA ANGGARAN")
        )
        
        output_anggaran_rincian = output_anggaran_rincian.to_pandas()
        output_anggaran_rincian["REALISASI ANGGARAN"] = output_anggaran_rincian["REALISASI ANGGARAN"].map("{:,.0f}".format)
        output_anggaran_rincian["PAGU ANGGARAN"] = output_anggaran_rincian["PAGU ANGGARAN"].map("{:,.0f}".format)
        output_anggaran_rincian["SISA ANGGARAN"] = output_anggaran_rincian["SISA ANGGARAN"].map("{:,.0f}".format)
        
        output_anggaran_rincian = output_anggaran_rincian[['KODE TIMKER', 'KODE', 'URAIAN', 'PERSENTASE CAPAIAN', 'PERSENTASE REALISASI ANGGARAN',
                                                           'TARGET', 'SATUAN \n TARGET', 'CAPAIAN', 'PAGU ANGGARAN',
                                                           'REALISASI ANGGARAN', 'SISA ANGGARAN']]
        return ui.HTML(
            DT(output_anggaran_rincian.style.background_gradient(
                subset=["PERSENTASE CAPAIAN", "PERSENTASE REALISASI ANGGARAN"], 
                cmap="RdYlGn", 
                vmin=0, 
                vmax=100).format(precision=2),
                buttons=[
                    "pageLength",
                    {"extend": "csvHtml5", "title": "Realisasi Per Timker"},
                    {"extend": "excelHtml5", "title": "Realisasi Per Timker"},
                ],
            )
        )

app = App(app_ui, server)